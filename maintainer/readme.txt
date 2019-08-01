crawler_manager是爬虫管理器，第一次使用，请更新排行榜。
ameboxoff__pubpra_classify_list和homboxoff_list依赖Firefox浏览器，可以尝试更改为chrome，但是使用chrome可能会使homboxoff_list不稳定。

爬虫管理器工作原理：
    更新排行榜：删除数据库中所有排行榜集合，即名称包含'list'的集合，然后逐个运行排行榜爬虫
    如何确定应该爬取电影？
        遍历排行榜集合，获取每个document的movie_id的值组成集合，
        再遍历basic_info集合(电影基本信息集合)，获取所有document的movie_id组成集合。
        取两个集合的差集，得到的集合即需要爬取的电影的movie_id
    如何爬取电影信息？
        通过movie_id计算出豆瓣详情页链接，传给电影爬虫（movie_crawler），由电影爬虫爬取。

注意：豆瓣网找不到的电影，只保存movie_id, 无其他字段
      爬取不到的信息，字段值为空（例如movie_id: 2134037, 20514888）。
      