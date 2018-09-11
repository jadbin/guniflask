# coding=utf-8

from os.path import join
from collections import defaultdict
from keyword import iskeyword

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint, PrimaryKeyConstraint, ForeignKey
import inflect

from guniflask.utils.template import string_camelcase, string_lowercase_underscore

inflect_engine = inflect.engine()


class SqlToModelGenerator:
    def __init__(self, name, metadata, indent=4):
        self.name = name
        self.indent = ' ' * indent

        many_to_many_tables = set()
        many_to_many_links = defaultdict(list)
        for table in metadata.tables.values():
            fk_constraints = [i for i in table.constraints if isinstance(i, ForeignKeyConstraint)]
            if len(fk_constraints) == 2 and len(table.columns) == 2 and all(col.foreign_keys for col in table.columns):
                many_to_many_tables.add(table.name)
                tablename = fk_constraints[0].elements[0].column.table.name
                many_to_many_links[tablename].append(table)

        self.models = {}
        for table in metadata.sorted_tables:
            if table.name in many_to_many_tables:
                continue
            self.models[table.name] = Model(table, many_to_many_links[table.name])

            # Add many-to-one relations
            for constraint in table.constraints:
                if isinstance(constraint, ForeignKeyConstraint):
                    tablename = constraint.elements[0].column.table.name
                    self.models[tablename].add_many_to_one_relation(constraint)

    def render(self, path):
        with open(join(path, '__init__.py'), 'w', encoding='utf-8') as f:
            f.write('# coding=utf-8\n')
        for model in self.models.values():
            model_name = convert_to_valid_identifier(model.table.name)
            with open(join(path, model_name + '.py'), 'w', encoding='utf-8') as f:
                f.write('# coding=utf-8\n\n')
                f.write(self.render_imports())
                tables_content = self.render_secondary_tables(model)
                if tables_content:
                    f.write('\n')
                    f.write(tables_content)
                f.write('\n\n')
                f.write(self.render_model(model))

    def render_imports(self):
        return 'from {} import db\n'.format(self.name)

    def render_model(self, model):
        header_str = "class {}(db.Model):\n".format(model.class_name)
        header_str += "{}__tablename__ = '{}'\n\n".format(self.indent, model.table.name)
        columns_str = ''
        for c in model.table.columns:
            columns_str += '{}{} = {}\n'.format(self.indent, convert_to_valid_identifier(c.name),
                                                self.render_column(c))
        relationships_str = ''
        for r in model.relationships:
            relationships_str += self.indent + self.render_relationship(r) + '\n'
        return header_str + columns_str + relationships_str

    def render_secondary_tables(self, model):
        return '\n'.join([self.render_table(r.association_table) for r in model.relationships
                          if isinstance(r, ManyToManyRelationship)])

    def render_table(self, table):
        columns_str = ',\n'.join(self.indent + self.render_column(c) for c in table.columns)
        return '{} = db.Table({},\n{}\n)\n'.format(convert_to_valid_identifier(table.name),
                                                   repr(table.name), columns_str)

    def render_column(self, column):
        is_sole_pk = column.primary_key and len(column.table.primary_key) == 1
        dedicated_fks = [c for c in column.foreign_keys if len(c.constraint.columns) == 1]
        is_unique = any(isinstance(c, UniqueConstraint) and set(c.columns) == {column}
                        for c in column.table.constraints)
        is_unique = is_unique or any(i.unique and set(i.columns) == {column}
                                     for i in column.table.indexes)
        has_index = any(set(i.columns) == {column} for i in column.table.indexes)

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

        kwargs_str = ''
        for k in kwargs:
            kwargs_str += ', {}={}'.format(k, repr(getattr(column, k)))
        return "db.Column({})".format(', '.join([self.render_column_type(column)] +
                                                [self.render_constraint(x) for x in dedicated_fks] +
                                                ['{}={}'.format(i, repr(getattr(column, i))) for i in kwargs]))

    @staticmethod
    def render_column_type(column):
        return 'db.{}'.format(repr(column.type))

    @staticmethod
    def render_constraint(constraint):
        def render_fk_options(*args):
            opts = [repr(i) for i in args]
            for attr in 'ondelete', 'onupdate':
                value = getattr(constraint, attr, None)
                if value:
                    opts.append('{}={}'.format(attr, repr(value)))
            return ', '.join(opts)

        if isinstance(constraint, ForeignKey):
            remote_column = '{}.{}'.format(constraint.column.table.name,
                                           constraint.column.name)
            return 'db.ForeignKey({})'.format(render_fk_options(remote_column))

    def render_relationship(self, relationship):
        kwargs_str = ', '.join([repr(relationship.target_cls)] +
                               ['{}={}'.format(i, relationship.kwargs[i]) for i in
                                sorted(relationship.kwargs.keys())])
        return '{} = db.relationship({})'.format(relationship.preferred_name, kwargs_str)


def convert_to_valid_identifier(name):
    name = string_lowercase_underscore(name)
    if name[0].isdigit() or iskeyword(name):
        name = '_' + name
    return name


class Model:
    parent_name = 'db.Model'

    def __init__(self, table, association_tables):
        self.table = table
        self.class_name = self.table_name_to_class_name(table.name)
        self.relationships = []

        # Add many-to-many relationships
        for association_table in association_tables:
            fk_constraints = [c for c in association_table.constraints if isinstance(c, ForeignKeyConstraint)]
            target_cls = self.table_name_to_class_name(fk_constraints[1].elements[0].column.table.name)
            relationship = ManyToManyRelationship(self.class_name, target_cls, association_table)
            self.relationships.append(relationship)

    @staticmethod
    def table_name_to_class_name(table_name):
        name = string_camelcase(table_name)
        if name[0].isdigit():
            name = '_' + name
        return name

    def add_many_to_one_relation(self, constraint):
        target_cls = self.table_name_to_class_name(constraint.table.name)
        relationship = ManyToOneRelationship(self.class_name, target_cls, constraint)
        self.relationships.append(relationship)


class Relationship:
    def __init__(self, source_cls, target_cls):
        self.source_cls = source_cls
        self.target_cls = target_cls
        self.kwargs = {}
        self.preferred_name = None


class ManyToOneRelationship(Relationship):
    def __init__(self, source_cls, target_cls, constraint):
        super().__init__(source_cls, target_cls)

        self.preferred_name = convert_to_valid_identifier(target_cls)
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
            repr(convert_to_valid_identifier(source_cls)))


class ManyToManyRelationship(Relationship):
    def __init__(self, source_cls, target_cls, association_table):
        super().__init__(source_cls, target_cls)

        self.preferred_name = inflect_engine.plural(convert_to_valid_identifier(target_cls))
        self.association_table = association_table

        self.kwargs['secondary'] = repr(convert_to_valid_identifier(association_table.name))
        self.kwargs['lazy'] = repr('select')
        self.kwargs['backref'] = "db.backref({}, lazy='select')".format(
            repr(inflect_engine.plural(convert_to_valid_identifier(source_cls))))
