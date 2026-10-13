CREATE OR ALTER PROCEDURE [dbo].[Comment_Create]
    @CommentID INT,
    @PostID INT = NULL,
    @UserID INT = NULL,
    @Content NVARCHAR(MAX) = NULL,
    @Timestamp DATETIME2(7) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    INSERT INTO [dbo].[Comment] ([CommentID], [PostID], [UserID], [Content], [Timestamp])
    OUTPUT INSERTED.[CommentID], INSERTED.[PostID], INSERTED.[UserID], INSERTED.[Content], INSERTED.[Timestamp]
    VALUES (@CommentID, @PostID, @UserID, @Content, @Timestamp);
END;
