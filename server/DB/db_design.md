# user.db
## auth_info
- id : TEXT PRIMARY KEY
- name : TEXT NOT NULL
- password : TEXT NOT NULL
- position : TEXT NOT NULL DEFAULT "normal"

## settings
- id : TEXT PRIMARY KEY
- open_code : NUMBER NOT NULL DEFAULT 0

# contest.db
## contest
- id : TEXT PRIMARY KEY
- name : TEXT NOT NULL
- start_time : DATETIME NOT NULL
- end_time : DATETIME NOT NULL
- problems : TEXT NOT NULL DEFAULT ""
- rate_limit : REAL NOT NULL DEFAULT 9999.0

# problem.db
## problem
- id : TEXT PRIMARY KEY
- name : TEXT NOT NULL
- scoring : NUMBER NOT NULL
- open_time : DATETIME NOT NULL
- lang_rest : TEXT NOT NULL

## submission
- id : TEXT PRIMARY KEY
- user_id : TEXT NOT NULL
- problem_id : TEXT NOT NULL
- date : DATETIME NOT NULL
- lang : TEXT NOT NULL
- status : NUMBER NOT NULL
- detail : TEXT NOT NULL DEFAULT ""
- score : NUMBER NOT NULL

## status
- id : NUMBER PRIMARY KEY
- name : TEXT NOT NULL

# rate.db
## rate
- user_id : TEXT PRIMARY KEY
- contest_id : TEXT PRIMARY KEY
- single_rate : REAL NOT NULL
- total_rate : REAL NOT NULL
