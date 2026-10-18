Analyze this project's database schema and data access code.

Project root: {project_root}
File inventory: {inventory_csv_path}

Read the inventory CSV; paths are relative to the project root. Inspect
eligible=true candidates, including the bodies of all CRUD procedures and methods.
Eligibility and filenames alone do not establish a file's purpose or behavior.

Write schema.md in the project root with one project-specific H1 and exactly
these H2 headings, in order. Use H3 or deeper for subsections.

```markdown
# <Project> database schema

## Scope and engine

## Structure

## Population
```

If schema.md exists, preserve its title and source-verified information, nesting
existing schema descriptions under Structure. Source files remain authoritative.

Scope and engine: identify engines, databases/namespaces, analyzed sources, setup,
and migration order where determinable. State that no live database was inspected.

Structure: organize by table or collection and document:

- Purpose, source paths, and fields with native types, nullability/optionality,
  defaults, generated values, keys, indexes, and validation constraints.
- Relationships, participating fields, and cardinality; distinguish declared
  constraints from inferred relationships and note ambiguities or conflicts.
- MongoDB nesting, arrays, embedding, and references without implying foreign-key
  enforcement.

Population: organize by table or collection. Analyze each create/insert, read,
update, and delete procedure or method individually. Include:

- Qualified name, operation, source path, and affected entities/fields.
- A parameter table: exact names, native types, required arguments, NULL/omission
  handling, defaults, and field mappings. Required does not mean non-null;
  parameter defaults are not column defaults.
- Returned values/result sets, side effects, validation, and errors.

Document source-defined transaction behavior and whether setup scripts install
the procedures.

For MongoDB, document equivalent application operations and embedding/reference
handling. If an interface is absent, say so. Do not invent procedures or methods.

Keep the document concise: use compact tables, state shared behavior once, and
record per-operation differences. Do not copy source bodies or repeat schema
tables. Report missing definitions, unsupported assumptions, and unresolved issues.
Write only schema.md. Do not execute database commands or include diagrams.
