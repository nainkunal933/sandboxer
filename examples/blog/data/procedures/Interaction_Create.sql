CREATE OR ALTER PROCEDURE [dbo].[Interaction_Create]
    @InteractionID INT,
    @UserID INT = NULL,
    @PostID INT = NULL,
    @Type NVARCHAR(50) = NULL,
    @Timestamp DATETIME2(7) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    INSERT INTO [dbo].[Interaction] ([InteractionID], [UserID], [PostID], [Type], [Timestamp])
    OUTPUT INSERTED.[InteractionID], INSERTED.[UserID], INSERTED.[PostID], INSERTED.[Type], INSERTED.[Timestamp]
    VALUES (@InteractionID, @UserID, @PostID, @Type, @Timestamp);
END;
