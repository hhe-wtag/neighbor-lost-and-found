Neighborhood Lost-and-Found — Database Schema

Use DBML to define your database structure

Docs: https://dbml.dbdiagram.io/docs

Render at: https://dbdiagram.io

```bash
Table users {
  id integer [primary key]
  name varchar
  email varchar [unique]
  hashed_password varchar
  role varchar [note: 'user | admin']
  contact_pref varchar [note: 'message | email | both']
  is_active boolean
  is_verified boolean
  created_at timestamp
  updated_at timestamp
}

Table items {
  id integer [primary key]
  user_id integer [ref: > users.id]
  type varchar [note: 'lost | found']
  title varchar
  description text
  category varchar [note: 'electronics | pets | keys | wallet | bag | documents | clothing | jewelry | other']
  date_occurred date
  lat decimal
  lng decimal
  location_name varchar
  status varchar [note: 'open | claimed | resolved | archived | removed']
  is_archived boolean
  expires_at timestamp
  created_at timestamp
  updated_at timestamp
}

Table photos {
  id integer [primary key]
  item_id integer [ref: > items.id]
  url varchar
  storage_type varchar [note: 'local | s3']
  mime_type varchar
  file_size_kb integer
  created_at timestamp
}

Table claims {
  id integer [primary key]
  item_id integer [ref: > items.id]
  user_id integer [ref: > users.id]
  message text
  status varchar [note: 'pending | approved | rejected']
  reviewed_at timestamp
  created_at timestamp
  updated_at timestamp
}

Table messages {
  id integer [primary key]
  item_id integer [ref: > items.id]
  from_user_id integer [ref: > users.id]
  to_user_id integer [ref: > users.id]
  body text
  is_read boolean
  created_at timestamp
}

Table reports {
  id integer [primary key]
  item_id integer [ref: > items.id]
  reporter_id integer [ref: > users.id]
  reviewed_by integer [ref: > users.id]
  reason varchar [note: 'spam | inappropriate | duplicate | scam | other']
  details text
  status varchar [note: 'pending | reviewed | actioned | dismissed']
  reviewed_at timestamp
  created_at timestamp
}
```

![DB DIAGRAM](https://raw.githubusercontent.com/hhe-wtag/neighbor-lost-and-found/refs/heads/project-specification/dbdiagram.png)
