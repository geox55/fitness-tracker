# Commit Review — Examples

## Example: Last 3 commits, no extra context

**User**

> Сделай ревью моих последних коммитов и скажи, нормально ли они сгруппированы.

**Agent (high-level structure)**

```markdown
## Commit review — overview

- Analyzed commits: 3 (HEAD..HEAD~2)
- Overall message quality: mostly clear, 1 commit has vague summary.
- Overall relevance: high, но есть немного рефакторинга, который лучше вынести отдельно.

### Commit a1b2c3d — feat(workouts): add workout creation page

**Summary**
- Implements new workout creation page in the frontend and wires it to the backend API.

**Problems**
- No major problems found.

**Suggestions**
- Consider mentioning the user-facing impact in the summary (e.g. “allow users to create workouts”).

**Relevance/Grouping**
- Relevance: High
- Grouping: Good — все изменения относятся к одной фиче.

### Commit e4f5g6h — refactor(workouts): clean up workout form

**Summary**
- Simplifies the workout form component and extracts shared hooks.

**Problems**
- Includes a few formatting-only changes in unrelated files.

**Suggestions**
- Move pure formatting changes to a separate `style` or `refactor` commit to keep this one focused.

**Relevance/Grouping**
- Relevance: Medium — формально относится к workouts, но содержит шумовые изменения.
- Grouping: Could be improved — лучше вынести форматирование отдельно.

### Commit i7j8k9l — chore: update dependencies

**Summary**
- Bumps frontend dependencies and updates Vite config.

**Problems**
- Commit message is a bit generic; не ясно, какие именно пакеты критичны.

**Suggestions**
- Уточнить, какие ключевые пакеты обновлены (например: “update react-query and eslint configs”).

**Relevance/Grouping**
- Relevance: High — все изменения относятся к зависимостям и конфигу.
- Grouping: Acceptable — изменения однородные.

## Overall recommendations

- Try to separate formatting-only changes into dedicated `style`/`refactor` commits.
- Make commit messages slightly more specific about user-facing impact and key dependencies.
```

