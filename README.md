# ActivityCacheParser

**ActivityCacheParser** is a python tool to extract forensics data from ActivityCache.db (Windows Activity Timeline).

The database is located at `C:\Users\<user>\AppData\ConnectedDevicesPlatform\<folder>\ActivitiesCache.db`.

`<folder>` can be any of the following based on the following:

+ Local user account: L.< local user account name > (e.g., “L.nihith)
+ Microsoft account: Microsoft ID number (e.g., “cdd048cc6c17532e”)
+ Azure Active Directory account: AAD.XXXXX


## References

1. https://www.cellebrite.com/en/exploring-the-windows-activity-timeline-part-1-the-high-points/
2. https://blog.group-ib.com/windows10_timeline_for_forensics
3. https://kacos2000.github.io/WindowsTimeline/WindowsTimeline.pdf

## Authors 👥

**B. K. S. Nihith**

+ Twitter: [@_Nihith](https://twitter.com/_Nihith)
+ Personal Blog: https://g4rud4.gitlab.io
+ Mail: [bolisettynihith@gmail.com](mailto:bolisettynihith@gmail.com)
