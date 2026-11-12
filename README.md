# The Cutest

A soft, warm frame built around charm rather than noise: rounded shapes, gentle color, and a focal point that invites a second look. The composition keeps plenty of breathing room so the character still reads instantly at feed size.

## Run

```
python3 main.py
```

Writes `entry.png` into `$MAKEFUN_OUTPUT_DIR` (default `/output`). No third-party
dependencies, standard library only.

## Note on the artwork

`entry.png` is **not** generated at runtime. It was drawn ahead of time by `art.py`,
which is included in this repository as the source of the artwork. `main.py` only
copies the already-rendered file, so the submission is byte-for-byte the art that
`art.py` produced.

## License

MIT - see [LICENSE](LICENSE).
