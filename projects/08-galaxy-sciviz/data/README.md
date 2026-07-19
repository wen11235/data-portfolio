# Data source

Dataset: [TipsyGalaxy](https://yt-project.org/data/TipsyGalaxy.tar.gz) — sample data from the [yt-project](https://yt-project.org/) data archive.

Direct download used by the notebook:
```
https://yt-project.org/data/TipsyGalaxy.tar.gz
```

Not committed to the repo (~11MB compressed). To reproduce:
```bash
curl -L -o TipsyGalaxy.tar.gz "https://yt-project.org/data/TipsyGalaxy.tar.gz"
tar -xzf TipsyGalaxy.tar.gz
```

Extracts to `TipsyGalaxy/galaxy.00300` (the simulation snapshot, Tipsy binary format) plus a `.FeMassFrac` sidecar file and a `.param` file. Loaded with `yt.load("TipsyGalaxy/galaxy.00300")`.
