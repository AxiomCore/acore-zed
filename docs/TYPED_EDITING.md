# Test standard typed editing in Zed

Z3 passed on macOS ARM64 with Zed 1.22.0 and a separately verified native
`acore-lsp`. Install/rebuild the dev extension using [INSTALL.md](INSTALL.md),
then configure the native path and language-server formatter using
[SETTINGS.md](SETTINGS.md). The extension does not supply a server download yet.

For a small configuration test, create `types.acore`:

```acore
class Settings { enabled: Boolean = true }
```

Beside it, create `main.acore`:

```acore
amends "types.acore"
label: String = "é😀"
count: Int = 1
flag: Boolean = false
settings: Settings = Settings { enabled = false }
transform = (value: Int) -> value + count
result = transform(2)
text = "count" // count stays in text
maximum = math.max(1, 2)
```

Use the command palette to select these exact actions. Recent similar actions
can rank above the requested action, and Vim mode changes the keyboard bindings.

1. Replace `false` with a `t` prefix and invoke **editor: show completions**.
   Select `true`; the compiler filters this Boolean position.
2. Inside `math.max` before the second argument, invoke **editor: show signature
   help**. The active parameter is `y: Number`. Move outside the call and no
   signature is expected.
3. Hover `Settings`; **editor: go to definition** opens `types.acore`.
   On the `settings` binding, **editor: go to type definition** reaches the class.
4. On the class, **editor: find all references** shows its declaration and uses.
   **outline: toggle** searches the buffer's grammar outline. **project symbols:
   toggle** searches native workspace symbols.
5. Rename the class to `Options`. Zed updates the declaration and both type uses.
   Rename `count` to `counter`; the string/comment stay unchanged. Renaming it
   to the existing `flag` must fail. Cross-file edits appear in a multibuffer;
   review them, then save the affected buffers. Undo cancels an unwanted edit.
6. Change the value of `flag` to `"oops"` and inspect the Boolean type error.
   Undo it and verify the diagnostic clears without saving. For a typo fix,
   create a separate `quickfix.acore` with `count: Int = 1` and
   `result = coun + 1`, then invoke **editor: toggle code actions** and apply the
   offered `count` repair. Repaired or unrelated diagnostics must not keep an
   old action alive.
7. Put an unindented property inside a class and invoke **editor: format** twice.
   The first pass fixes indentation; the second is stable. Test a CRLF file and
   keep the accented/emoji string and comments intact. Native formatting is
   conservative; arbitrary operator spacing is not normalized.
8. Leave a valid edit unsaved, invoke **editor: restart language server**, and
   confirm the text, completion and diagnostics remain current. Startup options
   require this recovery check, not just a running process.

For domain checks, open a complete project with its owning `AxiomDeps.toml`
and physical imports. Choose frontend/database entries explicitly when the
project has more than one candidate. The internal maintainer fixtures are kept
outside this adapter repository.

| Profile | Repeatable authoring checks |
| --- | --- |
| Backend | Complete a `response(type: …)` contract type; display the `response` signature; navigate an entity to its physical model. Rename an authored model and inspect the generated entity-reference update. A bad `CacheStrategy` enum offers validated replacements; arbitrary parser errors may have no fix. |
| Frontend | At `on_press`, complete an action and ensure an integer state binding is excluded. A wrong binding produces unsaved type diagnostics. Navigate/rename an imported authored component; display its signature inside the call. A unique one-character binding typo can offer a repair. Builtin component overload signatures are limited. |
| Database | At `foreignKey(... onDelete: …)`, complete `ReferenceAction` members and inspect the active signature parameter. Navigate physical schema/table/enum declarations and rename authored columns or imported schemas. A `DatabaseEngine` value in `onDelete` is rejected. These checks do not contact PostgreSQL or apply migrations. |

Open a child backend project with its own manifest and distinct model name;
definition/type navigation must resolve within that child owner. Search each
profile's unsaved renamed symbol through workspace search. Save before comparing
with the explicit [CLI checks](CLI.md): those read saved files.

Use `semantic_tokens: "combined"` for normal authoring. The Z3 acceptance also
used `"full"` temporarily to observe compiler colors independently of syntax
queries. Token colors depend on the theme. [Zed language configuration](https://zed.dev/docs/configuring-languages).

See [FEATURES.md](FEATURES.md) and the completed
[E7/configuration checks](E7_CONFIGURATION.md) for file renames, hint lifecycle
and explicit hierarchy/manifest/virtual-view limits. Real-Zed task acceptance
is Z5. Linux, Windows and physical Intel macOS acceptance remain pending.
