## Description

<!-- Briefly describe what this PR does. -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] New source (adapter)
- [ ] Documentation / README translation
- [ ] CI / infrastructure
- [ ] Other

## Checklist

- [ ] I have run `deuseek doctor` and attached output (if touching sources or fetch backends).
- [ ] New adapters implement `AdapterBase` (`is_ready` + `search` returning `list[SearchResult]`).
- [ ] New sources are registered in `deuseek/sources.yml`.
- [ ] I have run `pytest tests/ -v` and all tests pass.