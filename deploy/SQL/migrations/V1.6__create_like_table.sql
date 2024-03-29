CREATE TYPE reaction_type AS ENUM ('like', 'dislike');
CREATE TABLE reactions
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT now()::TIMESTAMPTZ,
    last_modified_at TIMESTAMPTZ DEFAULT now()::TIMESTAMPTZ,
    post_id          UUID NOT NULL,
    user_id          UUID NOT NULL,
    reaction         BOOLEAN     DEFAULT TRUE,
    FOREIGN KEY (post_id) REFERENCES posts (id),
    FOREIGN KEY (user_id) REFERENCES user_accounts (id)
);