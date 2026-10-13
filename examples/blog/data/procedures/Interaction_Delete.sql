CREATE OR ALTER PROCEDURE [dbo].[Interaction_Delete]
    @InteractionID INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DELETE FROM [dbo].[Interaction]
    OUTPUT DELETED.[InteractionID]
    WHERE [InteractionID] = @InteractionID;

    IF @@ROWCOUNT = 0
        THROW 50001, 'Interaction was not found.', 1;
END;
