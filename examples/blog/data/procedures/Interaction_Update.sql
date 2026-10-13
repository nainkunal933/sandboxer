-- Replaces all non-key fields; pass NULL explicitly to clear a nullable field.
CREATE OR ALTER PROCEDURE [dbo].[Interaction_Update]
    @InteractionID INT,
    @UserID INT,
    @PostID INT,
    @Type NVARCHAR(50),
    @Timestamp DATETIME2(7)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE [dbo].[Interaction]
    SET [UserID] = @UserID,
        [PostID] = @PostID,
        [Type] = @Type,
        [Timestamp] = @Timestamp
    OUTPUT INSERTED.[InteractionID], INSERTED.[UserID], INSERTED.[PostID], INSERTED.[Type], INSERTED.[Timestamp]
    WHERE [InteractionID] = @InteractionID;

    IF @@ROWCOUNT = 0
        THROW 50001, 'Interaction was not found.', 1;
END;
