begin transaction;

create table tags
(
    tag_id integer primary key asc,
    name varchar unique not null
);

create table taggings
(
    tag_id integer,
    md5 varchar,
    foreign key(md5) references zipballs(md5),
    foreign key(tag_id) references tags(id),
    unique (tag_id, md5) on conflict ignore
);

-- Add a column that will hold cached tag values
alter table zipballs add column tags varchar;

commit transaction;
