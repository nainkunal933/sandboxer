Analyze the database schema defined in this project.

Project root: {project_root}
File inventory: {inventory_csv_path}

Read the inventory CSV. Paths are relative to the project root.
Inspect files marked eligible=true to identify database definitions.
Eligibility indicates a candidate file, not a confirmed schema source.

Create schema.md in the project root, documenting:

1. Database engines identified from the source files.
2. Tables and collections, including their purpose where evident.
3. Fields, native types, nullability or optionality, defaults,
   and validation constraints.
4. Primary keys, unique constraints, and indexes.
5. Relationships and cardinality where supported by the definitions.
6. For MongoDB, nested documents, arrays, embedded entities,
   and document references.

Include source file paths for each documented entity.
Distinguish explicitly declared constraints from inferred relationships.
Do not treat MongoDB references as enforced foreign keys.
Do not invent missing definitions. Record ambiguities and conflicts.
If migrations exist, account for their ordering where determinable.

If no database definitions are found, document that finding.
Write only schema.md; leave source files unchanged.
Do not include a diagram or generate sandbox data at this stage.
