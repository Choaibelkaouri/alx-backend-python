# 0. Getting started with Python generators — seeding DB

This step seeds a MySQL database we’ll use later with a generator that streams rows one by one.

## Objective

Create a seed script that:

- Creates a MySQL database `ALX_prodev`
- Creates a `user_data` table with the required schema
- Populates it from `user_data.csv`

## Schema

- `user_id` `CHAR(36)` **PRIMARY KEY**, **INDEXED** (UUID)
- `name` `VARCHAR(255)` **NOT NULL**
- `email` `VARCHAR(255)` **NOT NULL**
- `age` `DECIMAL(5,0)` **NOT NULL**

## Layout

