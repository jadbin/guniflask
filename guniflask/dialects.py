# coding=utf-8

import inspect

import sqlalchemy


class DatabaseDialect:
    def convert_column_type(self, coltype):
        raise NotImplementedError

    def get_kwargs(self, coltype):
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


class MysqlDialect(DatabaseDialect):
    name = 'mysql'

    column_types = {
        'VARCHAR': sqlalchemy.String,
        'TEXT': sqlalchemy.Text,
        'BOOLEAN': sqlalchemy.Boolean,
        'TINYINT': sqlalchemy.SmallInteger,
        'SMALLINT': sqlalchemy.SmallInteger,
        'INTEGER': sqlalchemy.Integer,
        'BIGINT': sqlalchemy.BigInteger,
        'FLOAT': sqlalchemy.Float,
        'DOUBLE': sqlalchemy.Float,
        'DECIMAL': sqlalchemy.DECIMAL,
        'ENUM': sqlalchemy.Enum,
        'DATE': sqlalchemy.Date,
        'DATETIME': sqlalchemy.DateTime,
        'TIMESTAMP': sqlalchemy.TIMESTAMP
    }

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
            kwargs = self.get_kwargs(coltype)
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


supported_dialects = {
    MysqlDialect.name: MysqlDialect()
}
