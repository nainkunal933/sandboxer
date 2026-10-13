IF OBJECT_ID(N'dbo.Comment', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[Comment] (
        [CommentID] INT NOT NULL,
        [PostID] INT NULL,
        [UserID] INT NULL,
        [Content] NVARCHAR(MAX) NULL,
        [Timestamp] DATETIME2(7) NULL,
        CONSTRAINT [PK_Comment] PRIMARY KEY ([CommentID]),
        CONSTRAINT [FK_Comment_Post] FOREIGN KEY ([PostID])
            REFERENCES [dbo].[Post] ([PostID]),
        CONSTRAINT [FK_Comment_User] FOREIGN KEY ([UserID])
            REFERENCES [dbo].[User] ([UserID])
    );
END;
