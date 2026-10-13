-- Replaces all non-key fields; pass NULL explicitly to clear a nullable field.
CREATE OR ALTER PROCEDURE [dbo].[Post_Update]
    @PostID INT,
    @Title NVARCHAR(255),
    @Content NVARCHAR(MAX),
    @Category NVARCHAR(100),
    @PublicationDate DATETIME2(7),
    @Tags NVARCHAR(255)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE [dbo].[Post]
    SET [Title] = @Title,
        [Content] = @Content,
        [Category] = @Category,
        [PublicationDate] = @PublicationDate,
        [Tags] = @Tags
    OUTPUT INSERTED.[PostID], INSERTED.[Title], INSERTED.[Content], INSERTED.[Category], INSERTED.[PublicationDate], INSERTED.[Tags]
    WHERE [PostID] = @PostID;

    IF @@ROWCOUNT = 0
        THROW 50001, 'Post was not found.', 1;
END;
