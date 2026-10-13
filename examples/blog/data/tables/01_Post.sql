IF OBJECT_ID(N'dbo.Post', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[Post] (
        [PostID] INT NOT NULL,
        [Title] NVARCHAR(255) NULL,
        [Content] NVARCHAR(MAX) NULL,
        [Category] NVARCHAR(100) NULL,
        [PublicationDate] DATETIME2(7) NULL,
        [Tags] NVARCHAR(255) NULL,
        CONSTRAINT [PK_Post] PRIMARY KEY ([PostID])
    );
END;
