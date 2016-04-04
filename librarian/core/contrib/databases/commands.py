

def dump_tables(arg, supervisor):
    schema = []
    for db in supervisor.exts.databases.values():
        db.query(db.Select('*', sets='sqlite_master'))
        for r in db.results:
            if r.type == 'table':
                schema.append(r.sql)
        print('\n'.join(schema))

    raise supervisor.EarlyExit()
