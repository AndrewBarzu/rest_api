create table Users (
id varchar(28) primary key,
name varchar(20),
surname varchar(50),
email varchar(50) unique,
university varchar(100),
)

create table Groups (
id int primary key identity,
name varchar(20),
description varchar(150)
)

create table Members(
uid varchar(28) foreign key references Users(id),
gid int foreign key references Groups(id),
is_admin bit,
constraint PK_constraint primary key (uid, gid)
)

create table Reminders(
id int primary key identity,
description varchar(150),
uid varchar(28) foreign key references Users(id)
)

create table Posts(
id int primary key identity,
gid int foreign key references Groups(id),
uid varchar(28) foreign key references Users(id),
title varchar(40),
body varchar(300),
post_time datetime2
)

drop table Assignments

create table Assignments(
id int primary key identity,
uid varchar(28) foreign key references Users(id),
name varchar(30),
description varchar(150),
due_date datetime2
)

drop trigger UserDeleteTrigger

go
create trigger UserDeleteTrigger on Users
instead of delete
as
begin
	delete from Members
	where uid in (select id from deleted)
	delete from Posts
	where uid in (select id from deleted)
	delete from Assignments
	where uid in (select id from deleted)
	delete from Reminders
	where uid in (select id from deleted)
	delete from Groups
	where id in (select gid from Members where uid = (select id from deleted) and is_admin = 1)
	delete from Users
	where id in (select id from deleted)
end
go

drop trigger GroupDeleteTrigger
go
create trigger GroupDeleteTrigger on Groups
instead of delete
as
begin
	delete from Members
	where gid in (select id from deleted)
	delete from Posts
	where gid in (select id from deleted)
	delete from Groups
	where id in (select id from deleted)
end
go

drop procedure delete_group

go
create procedure delete_group @uid varchar(28), @gid int
as
begin
	declare @count int;
	select @count=count(*) from (select * from Members as M where M.uid = @uid and M.gid = @gid and M.is_admin = 1) a;
	if (@count = 1)
	begin
		delete from Groups
		where Groups.id = @gid
	end
end
go

go
drop procedure add_member_to_group
go

go
create procedure add_member_to_group @uid varchar(28), @gid int, @other_uid varchar(28)
as
begin
	declare @count int;
	select @count=count(*) from (select * from Members as M where M.uid = @uid and M.gid = @gid and M.is_admin = 1) a;
	if (@count = 1)
	begin
		declare @new_user varchar(28);
		select @new_user=a.id from (select U.id from Users as U where U.id = @other_uid) a;
		insert into Members (uid, gid, is_admin) values (@new_user, @gid, 0);
	end
end
go

drop procedure remove_member_from_group

go
create procedure remove_member_from_group @uid varchar(28), @gid int, @other_uid varchar(28)
as
begin
	declare @count int;
	select @count=count(*) from (select * from Members as M where M.uid = @uid and M.gid = @gid and M.is_admin = 1) a;
	if (@count = 1)
	begin
		delete from Members
		where uid = @other_uid and gid = @gid
	end
end
go
