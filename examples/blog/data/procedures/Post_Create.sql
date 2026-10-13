CREATE OR ALTER PROCEDURE [dbo].[Post_Create]
    @PostID INT,
    @Title NVARCHAR(255) = NULL,
    @Content NVARCHAR(MAX) = NULL,
    @Category NVARCHAR(100) = NULL,
    @PublicationDate DATETIME2(7) = NULL,
    @Tags NVARCHAR(255) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    INSERT INTO [dbo].[Post] ([PostID], [Title], [Content], [Category], [PublicationDate], [Tags])
    OUTPUT INSERTED.[PostID], INSERTED.[Title], INSERTED.[Content], INSERTED.[Category], INSERTED.[PublicationDate], INSERTED.[Tags]
    VALUES (@PostID, @Title, @Content, @Category, @PublicationDate, @Tags);
END;
