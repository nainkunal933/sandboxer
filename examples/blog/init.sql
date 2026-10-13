:ON ERROR EXIT

IF DB_ID(N'Blog') IS NULL
    CREATE DATABASE [Blog];
GO

USE [Blog];
GO

SET XACT_ABORT ON;
BEGIN TRANSACTION;

IF OBJECT_ID(N'dbo.Post', N'U') IS NULL
BEGIN
:r /schema/tables/01_Post.sql
END;

IF OBJECT_ID(N'dbo.User', N'U') IS NULL
BEGIN
:r /schema/tables/02_User.sql
END;

IF OBJECT_ID(N'dbo.Comment', N'U') IS NULL
BEGIN
:r /schema/tables/03_Comment.sql
END;

IF OBJECT_ID(N'dbo.Interaction', N'U') IS NULL
BEGIN
:r /schema/tables/04_Interaction.sql
END;

COMMIT TRANSACTION;
PRINT N'Blog database and tables are ready.';
GO
