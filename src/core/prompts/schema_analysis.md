Analyze this project's database schema and data access code.

Project root: {project_root}
File inventory: {inventory_csv_path}

Read the inventory CSV; paths are relative to the project root. Inspect
eligible=true candidates to identify schema definitions and data creation entry
points. Inspect create/insert procedure and method bodies fully. Inspect other
procedures and methods only enough to verify their qualified names, operations,
affected targets, and source paths for reference. Eligibility and filenames alone
do not establish a file's purpose or behavior.

Write .sandboxer/schema.md relative to the project root with one project-specific
H1 and exactly these H2 headings, in order. Use H3 or deeper for subsections.

```markdown
# <Project> database schema

## Database metadata

## Structure

## Population

## Procedure references
```

If .sandboxer/schema.md exists, preserve its title and source-verified schema and
creation information, nesting schema descriptions under Structure. Replace old
read/update/delete details with compact entries under Procedure references;
remove their parameter tables and detailed behavior, including shared behavior
that only concerns those operations. Replace any old Scope and engine section
with Database metadata and remove its scope narrative. Source files remain
authoritative.

Database metadata: include only these three entries:

- Data model: an exact enum value from the list below, formatted as inline code.
  Use an array of distinct enum values if multiple models are demonstrated.
  If classification cannot be established, state that it is undetermined rather
  than guessing or inventing an enum value.
- Engine: the source-identified database engine, or engines when multiple are
  demonstrated. State uncertainty when the engine cannot be determined.
- Databases: a JSON array of all explicitly identified database names,
  deduplicated in discovery order. Use [] when no names can be determined.
  Do not infer database names from directories or select a target database.
  Do not limit the number of databases or perform live database discovery.

Allowed data models and classification guidance:

{data_models}

Classify from the inspected schema structures and usage, not solely from the
database product or its supported features. Do not include scope narrative,
inventory counts, dependency versions, or setup/migration details in Database
metadata. Analysis describes the source schema without selecting a target.

Structure: organize by table or collection and document:

- Purpose, source paths, and fields with native types, nullability/optionality,
  defaults, generated values, keys, indexes, and validation constraints.
- Relationships, participating fields, and cardinality; distinguish declared
  constraints from inferred relationships and note ambiguities or conflicts.
- MongoDB nesting, arrays, embedding, and references without implying foreign-key
  enforcement.

Preserve source-qualified entity names where needed to distinguish identically
named entities across databases.

Population: organize by table or collection. Document only create/insert
procedures or methods individually. Include:

- Qualified name, operation, source path, and affected entities/fields.
- A parameter table: exact names, native types, required arguments, NULL/omission
  handling, defaults, and field mappings. Required does not mean non-null;
  parameter defaults are not column defaults.
- Returned values/result sets, side effects, validation, and errors.

Document source-defined creation transaction behavior and whether setup scripts
install the procedures. Keep shared behavior focused on creation.

For MongoDB, document equivalent application creation operations and
embedding/reference handling. If a creation interface is absent, say so. Do not
invent procedures or methods.

Procedure references: list other procedures or methods, including read, update,
and delete, in a compact table with target, qualified name, operation, and source
path. These are references for the agent to consult if needed; do not include
parameter tables, detailed behavior, or source bodies. Keep them out of Population
and out of the procedure files supplied to generate for copying.

Keep the document concise: use compact tables, state shared behavior once, and
record per-operation differences. Do not copy source bodies or repeat schema
tables. Report missing definitions, unsupported assumptions, and unresolved issues.
Write only .sandboxer/schema.md. Do not execute database commands or include
diagrams.
