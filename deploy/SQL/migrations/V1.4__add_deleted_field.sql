ALTER TABLE posts
    ADD COLUMN is_deleted TIMESTAMPTZ DEFAULT NULL;