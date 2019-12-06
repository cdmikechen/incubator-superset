# 汉化 Apache-Superset 0.35版本

1. 新增部分汉化信息，将部分组件支持文本翻译模式
2. 修复0.35版本一些问题（新增图表无法汉化等等）

汉化 `message.po` 文件的命令
```
po2json -d superset -f jed1.x superset/translations/zh/LC_MESSAGES/messages.po superset/translations/zh/LC_MESSAGES/messages.json
pybabel compile -d superset/translations
```

后续会不定期更新汉化信息
