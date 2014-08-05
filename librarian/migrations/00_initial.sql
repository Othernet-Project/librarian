create table migrations
(
    id primary_key unique default 0,  -- Record is singleton, always use 0
    version integer null
);

