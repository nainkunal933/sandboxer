CREATE TABLE [dbo].[Interaction] (
    [InteractionID] INT NOT NULL,
    [UserID] INT NULL,
    [PostID] INT NULL,
    [Type] NVARCHAR(50) NULL,
    [Timestamp] DATETIME2(7) NULL,
    CONSTRAINT [PK_Interaction] PRIMARY KEY ([InteractionID]),
    CONSTRAINT [FK_Interaction_User] FOREIGN KEY ([UserID])
        REFERENCES [dbo].[User] ([UserID]),
    CONSTRAINT [FK_Interaction_Post] FOREIGN KEY ([PostID])
        REFERENCES [dbo].[Post] ([PostID])
);
