# user.db
## auth_info
- id : TEXT PRIMARY KEY
- name : TEXT NOT NULL
- password : TEXT NOT NULL

## settings
- id : TEXT PRIMARY KEY
- open_code : NUMBER NOT NULL DEFAULT 0

# contest.db
## contest
- id : TEXT PRIMARY KEY
- name : TEXT NOT NULL
- start_time : TEXT NOT NULL
- end_time : TEXT NOT NULL

# problem.db
## problem
- id : TEXT PRIMARY KEY
- name : TEXT NOT NULL
- scoring : NUMBER NOT NULL
- open_time : TEXT NOT NULL

## submission
- id : TEXT PRIMARY KEY
- user_id : TEXT NOT NULL
- problem_id : TEXT NOT NULL
- date : TEXT NOT NULL
