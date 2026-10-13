IF OBJECT_ID(N'dbo.User', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[User] (
        [UserID] INT NOT NULL,
        [Username] NVARCHAR(50) NULL,
        [Email] NVARCHAR(255) NULL,
        -- Store password hashes here, never plaintext passwords.
        [Password] NVARCHAR(255) NULL,
        [Bio] NVARCHAR(MAX) NULL,
        [ProfilePicture] NVARCHAR(255) NULL,
        CONSTRAINT [PK_User] PRIMARY KEY ([UserID])
    );
END;
