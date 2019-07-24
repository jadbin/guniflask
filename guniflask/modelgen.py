# coding=utf-8

import os
from os.path import join, exists
from collections import defaultdict
from keyword import iskeyword
import re
import inspect

import sqlalchemy
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint, PrimaryKeyConstraint, CheckConstraint, ForeignKey
import inflect
from sqlalchemy.util import OrderedDict

from guniflask.utils.template import string_camelcase, string_lowercase_underscore

inflect_engine = inflect.engine()


class SqlToModelGenerator:
    def __init__(self, name, metadata, indent=4):
        dialect_name = metadata.bind.dialect.name
        if dialect_name not in supported_dialects:
            raise ValueError('Unsupported dialect: {}'.format(dialect_name))

        self.dialect = supported_dialects[dialect_name]
        self.name = name
        self.metadata = metadata
        self.indent = ' ' * indent

        many_to_many_tables = set()
        many_to_many_links = defaultdict(list)
        for table in metadata.tables.values():
            fk_constraints = [i for i in table.constraints if isinstance(i, ForeignKeyConstraint)]
            if len(fk_constraints) == 2 and all(col.foreign_keys for col in table.columns):
                many_to_many_tables.add(table.name)
                tablename = sorted(fk_constraints, key=get_constraint_sort_key)[0].elements[0].column.table.name
                many_to_many_links[tablename].append(table)

        self.models = {}
        for table in metadata.sorted_tables:
            if table.name in many_to_many_tables:
                continue
            self.models[table.name] = Model(table, many_to_many_links[table.name])

            # Add many-to-one relations
            for constraint in sorted(table.constraints, key=get_constraint_sort_key):
                if isinstance(constraint, ForeignKeyConstraint):
                    tablename = constraint.elements[0].column.table.name
                    self.models[tablename].add_many_to_one_relation(constraint)

    def render(self, path):
        if not exists(path):
            os.makedirs(path)
        model_modules = []
        for model in self.models.values():
            module_name = convert_to_valid_identifier(model.table.name)
            with open(join(path, module_name + '.py'), 'w', encoding='utf-8') as f:
                f.write('# coding=utf-8\n\n')
                f.write(self.render_imports(model))
                tables_content = self.render_secondary_tables(model)
                if tables_content:
                    f.write('\n')
                    f.write(tables_content)
                f.write('\n\n')
                f.write(self.render_model(model))
            model_modules.append({'module': module_name, 'class': model.class_name})
        with open(join(path, '__init__.py'), 'w', encoding='utf-8') as f:
            f.write('# coding=utf-8\n\n')
            for m in model_modules:
                f.write('from .{} import {}\n'.format(m['module'], m['class']))

    def render_imports(self, model):
        d = OrderedDict()
        for col in model.table.columns:
            if col.server_default:
                d.setdefault('sqlalchemy', ('text', '_text'))

        imports = ''
        for k, v in d.items():
            if isinstance(v, tuple):
                imports += 'from {} import {} as {}\n'.format(k, v[0], v[1])
            else:
                imports += 'from {} import {}\n'.format(k, v)
        if len(d) > 0:
            imports += '\n'
        imports += 'from {} import db\n'.format(self.name)
        return imports

    def render_model(self, model):
        header_str = "class {}(db.Model):\n".format(model.class_name)
        header_str += "{}__tablename__ = '{}'\n\n".format(self.indent, model.table.name)
        columns_str = ''
        for col in model.table.columns:
            attr = convert_to_valid_identifier(col.name)
            show_name = attr != col.name
            columns_str += '{}{} = {}\n'.format(self.indent, attr,
                                                self.render_column(col, show_name=show_name))
        relationships_str = ''
        for r in model.relationships:
            relationships_str += self.indent + self.render_relationship(r) + '\n'
        return header_str + columns_str + relationships_str

    def render_secondary_tables(self, model):
        return '\n'.join([self.render_table(r.association_table) for r in model.relationships
                          if isinstance(r, ManyToManyRelationship)])

    def render_table(self, table):
        columns_str = ',\n'.join(self.indent + self.render_column(col, show_name=True) for col in table.columns)
        tablename = convert_to_valid_identifier(table.name)
        return '{} = db.Table({!r},\n{}\n)\n'.format(tablename, table.name, columns_str)

    def render_column(self, column, show_name=False):
        is_sole_pk = column.primary_key and len(column.table.primary_key) == 1
        dedicated_fks = [c for c in column.foreign_keys if len(c.constraint.columns) == 1]
        is_unique = any(isinstance(c, UniqueConstraint) and set(c.columns) == {column}
                        for c in column.table.constraints)
        is_unique = is_unique or any(i.unique and set(i.columns) == {column}
                                     for i in column.table.indexes)
        has_index = any(set(i.columns) == {column} for i in column.table.indexes)
        server_default = None
        kwargs = []
        if column.key != column.name:
            kwargs.append('key')
        if column.primary_key:
            kwargs.append('primary_key')
        if column.autoincrement is True:
            kwargs.append('autoincrement')
        if not column.nullable and not is_sole_pk:
            kwargs.append('nullable')
        if is_unique:
            column.unique = True
            kwargs.append('unique')
        if has_index:
            column.index = True
            kwargs.append('index')
        if column.comment:
            kwargs.append('comment')
        if column.server_default:
            default_expr = self.get_compiled_expression(column.server_default.arg)
            if '\n' in default_expr:
                server_default = 'server_default=text("""\\\n{0}""")'.format(default_expr)
            else:
                default_expr = default_expr.replace('"', '\\"')
                server_default = 'server_default=_text("{0}")'.format(default_expr)
        extra_kwargs = self.get_extra_column_kwargs(column)
        return "db.Column({})".format(', '.join(([repr(column.name)] if show_name else []) +
                                                [self.render_column_type(column.type)] +
                                                [self.render_constraint(x) for x in dedicated_fks] +
                                                ['{}={!r}'.format(i, getattr(column, i)) for i in kwargs] +
                                                ([server_default] if server_default else []) +
                                                ['{}={}'.format(i, extra_kwargs[i]) for i in
                                                 sorted(extra_kwargs.keys())]))

    def get_extra_column_kwargs(self, column):
        kwargs = {}
        for p in supported_column_properties:
            if p.match_column(column):
                kwargs.update(p.kwargs)
        return kwargs

    def render_column_type(self, coltype):
        return 'db.{}'.format(self.dialect.convert_column_type(coltype))

    def render_constraint(self, constraint):
        def render_fk_options(*args):
            opts = [repr(i) for i in args]
            for attr in 'ondelete', 'onupdate':
                value = getattr(constraint, attr, None)
                if value:
                    opts.append('{}={!r}'.format(attr, value))
            return ', '.join(opts)

        if isinstance(constraint, ForeignKey):
            remote_column = '{}.{}'.format(constraint.column.table.name,
                                           constraint.column.name)
            return 'db.ForeignKey({})'.format(render_fk_options(remote_column))

    def render_relationship(self, relationship):
        kwargs_str = ', '.join([repr(table_name_to_class_name(relationship.target_tbl))] +
                               ['{}={}'.format(i, relationship.kwargs[i]) for i in
                                sorted(relationship.kwargs.keys())])
        return '{} = db.relationship({})'.format(relationship.preferred_name, kwargs_str)

    def get_compiled_expression(self, statement):
        return str(statement.compile(
            self.metadata.bind, compile_kwargs={"literal_binds": True}))


def convert_to_valid_identifier(name):
    name = string_lowercase_underscore(name)
    if name[0].isdigit() or iskeyword(name):
        name = '_' + name
    return name


def table_name_to_class_name(table_name):
    name = string_camelcase(table_name)
    if name[0].isdigit():
        name = '_' + name
    return name


def get_constraint_sort_key(constraint):
    if isinstance(constraint, CheckConstraint):
        return 'C{0}'.format(constraint.sqltext)
    return constraint.__class__.__name__[0] + repr(list(constraint.columns.keys()))


class Model:
    parent_name = 'db.Model'

    def __init__(self, table, association_tables):
        self.table = table
        self.class_name = table_name_to_class_name(table.name)
        self.relationships = []

        # Add many-to-many relationships
        for association_table in association_tables:
            fk_constraints = [c for c in association_table.constraints if isinstance(c, ForeignKeyConstraint)]
            fk_constraints.sort(key=get_constraint_sort_key)
            target_tbl = fk_constraints[1].elements[0].column.table.name
            relationship = ManyToManyRelationship(self.table.name, target_tbl, association_table)
            self.relationships.append(relationship)

    def add_many_to_one_relation(self, constraint):
        relationship = ManyToOneRelationship(self.table.name, constraint.table.name, constraint)
        self.relationships.append(relationship)


class Relationship:
    def __init__(self, source_tbl, target_tbl):
        self.source_tbl = source_tbl
        self.target_tbl = target_tbl
        self.kwargs = {}
        self.preferred_name = None


class ManyToOneRelationship(Relationship):
    def __init__(self, source_tbl, target_tbl, constraint):
        super().__init__(source_tbl, target_tbl)

        self.preferred_name = convert_to_valid_identifier(target_tbl)
        self.constraint = constraint

        # Add uselist=False to one-to-one relationships
        column_names = list(constraint.columns.keys())
        if any(isinstance(c, (PrimaryKeyConstraint, UniqueConstraint)) and
               set(col.name for col in c.columns) == set(column_names)
               for c in constraint.table.constraints):
            self.kwargs['uselist'] = 'False'

        if self.kwargs.get('uselist') is not False:
            self.preferred_name = inflect_engine.plural(self.preferred_name)
            self.kwargs['lazy'] = repr('select')
        else:
            self.kwargs['lazy'] = repr('joined')
        self.kwargs['backref'] = "db.backref({}, lazy='joined')".format(
            repr(convert_to_valid_identifier(source_tbl)))
        self.kwargs['cascade'] = repr('all, delete-orphan')


class ManyToManyRelationship(Relationship):
    def __init__(self, source_tbl, target_tbl, association_table):
        super().__init__(source_tbl, target_tbl)

        self.preferred_name = inflect_engine.plural(convert_to_valid_identifier(target_tbl))
        self.association_table = association_table

        self.kwargs['secondary'] = convert_to_valid_identifier(association_table.name)
        self.kwargs['lazy'] = repr('select')
        self.kwargs['backref'] = "db.backref({}, lazy='select')".format(
            repr(inflect_engine.plural(convert_to_valid_identifier(source_tbl))))


class ColumnProperty:
    def __init__(self):
        self.kwargs = {}

    def match_column(self, column):
        raise NotImplementedError


class CreatedTimeProperty(ColumnProperty):
    def __init__(self):
        super().__init__()
        self.kwargs['default'] = 'db.func.now()'
        self.reg = re.compile(r'^create[d]?_(time|at)$')

    def match_column(self, column):
        return isinstance(column.type, sqlalchemy.DateTime) and self.reg.match(column.name.lower()) is not None


class UpdatedTimeProperty(ColumnProperty):
    def __init__(self):
        super().__init__()
        self.kwargs['default'] = 'db.func.now()'
        self.kwargs['onupdate'] = 'db.func.now()'
        self.reg = re.compile(r'^update[d]?_(time|at)$')

    def match_column(self, column):
        return isinstance(column.type, sqlalchemy.DateTime) and self.reg.match(column.name.lower()) is not None


supported_column_properties = [CreatedTimeProperty(), UpdatedTimeProperty()]


class DatabaseDialect:
    column_types = {}

    def get_kwargs_of_column_type(self, coltype):
        argspec = inspect.getfullargspec(coltype.__class__.__init__)
        defaults = dict(zip(argspec.args[-len(argspec.defaults or ()):],
                            argspec.defaults or ()))
        kwargs = {}
        missing = object()
        for attr in argspec.args[1:]:
            value = getattr(coltype, attr, missing)
            default = defaults.get(attr, missing)
            if value is not missing and value != default:
                kwargs[attr] = value
        return kwargs

    def convert_column_type(self, coltype):
        coltype_name = coltype.__class__.__name__
        if coltype_name not in self.column_types:
            raise ValueError('Unsupported column type: {}'.format(coltype_name))
        column_type = self.column_types[coltype_name]

        args = []

        if issubclass(column_type, sqlalchemy.Enum):
            args.extend(repr(arg) for arg in coltype.enums)
            if coltype.name is not None:
                args.append('name={!r}'.format(coltype.name))
        else:
            # All other types
            kwargs = self.get_kwargs_of_column_type(coltype)
            argspec = inspect.getfullargspec(column_type.__init__)
            defaults = dict(zip(argspec.args[-len(argspec.defaults or ()):],
                                argspec.defaults or ()))
            missing = object()
            use_kwargs = False
            for attr in argspec.args[1:]:
                if attr.startswith('_'):
                    continue
                value = kwargs.get(attr, missing)
                default = defaults.get(attr, missing)
                if value is missing or value == default:
                    use_kwargs = True
                elif use_kwargs:
                    args.append('{}={!r}'.format(attr, value))
                else:
                    args.append(repr(value))
        rendered = column_type.__name__
        if args:
            rendered += '({})'.format(', '.join(args))
        return rendered


class MysqlDialect(DatabaseDialect):
    column_types = {
        'BIGINT': sqlalchemy.BigInteger,
        'BINARY': sqlalchemy.Binary,
        'BLOB': sqlalchemy.LargeBinary,
        'BOOLEAN': sqlalchemy.Boolean,
        'CHAR': sqlalchemy.CHAR,
        'DATE': sqlalchemy.Date,
        'DATETIME': sqlalchemy.DateTime,
        'DECIMAL': sqlalchemy.DECIMAL,
        'DOUBLE': sqlalchemy.Float,
        'ENUM': sqlalchemy.Enum,
        'FLOAT': sqlalchemy.Float,
        'INTEGER': sqlalchemy.Integer,
        'JSON': sqlalchemy.JSON,
        'SMALLINT': sqlalchemy.SmallInteger,
        'NUMERIC': sqlalchemy.Numeric,
        'TEXT': sqlalchemy.Text,
        'TIMESTAMP': sqlalchemy.TIMESTAMP,
        'TINYBLOB': sqlalchemy.Binary,
        'TINYINT': sqlalchemy.SmallInteger,
        'VARBINARY': sqlalchemy.VARBINARY,
        'VARCHAR': sqlalchemy.String,
    }


supported_dialects = {
    'mysql': MysqlDialect()
}
