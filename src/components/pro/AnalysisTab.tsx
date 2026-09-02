import React from 'react'
import { View, Text, Button } from '@tarojs/components'

interface AnalysisTabProps {
  stats: {
    recentScore: number;
    historyAvg: number;
    totalQuests: number;
    subjectBreakdown: any[];
    focusAreas: {
      name: string;
      avg: number;
      count: number;
      filters: any;
    }[];
    strongestSubject: { name: string; avg: number };
    weakestTopic: { name: string; avg: number; topic?: string };
    trendData: { label: string; value: number }[];
  };
  lang: string;
  t: any;
  wrongCount: number;
  trendFilter: string;
  setTrendFilter: (filter: string) => void;
  handleRedoWrong: () => void;
  startPracticeWithFilters: (filters: any) => void;
  getMetricColor: (val: number) => string;
  setActiveTab: (tab: number) => void;
}

export default function AnalysisTab({
  stats,
  lang,
  t,
  wrongCount,
  trendFilter,
  setTrendFilter,
  handleRedoWrong,
  startPracticeWithFilters,
  getMetricColor,
  setActiveTab
}: AnalysisTabProps) {
  const trendLabels = lang === 'zh'
    ? { 'Last Runs': '最近几轮', '7D': '7天', '30D': '30天', 'All Time': '全部' }
    : { 'Last Runs': 'Last Runs', '7D': '7D', '30D': '30D', 'All Time': 'All Time' }
  const questionUnit = lang === 'zh' ? '道题' : 'questions'

  if (stats.totalQuests === 0) {
    return (
      <View className="empty-stats-hero">
        <Text className="empty-emoji">📊</Text>
        <Text className="empty-title">{lang === 'zh' ? '暂无数据' : 'No Data Yet'}</Text>
        <Text className="empty-desc">
          {lang === 'zh'
            ? '完成第一次练习，解锁思维战力分析 🚀'
            : 'Complete your first practice to unlock Thinking Skills Insights 🚀'}
        </Text>
        <Button className="start-btn empty-start-btn" onClick={() => setActiveTab(0)}>
          {t.start_quest}
        </Button>
      </View>
    )
  }

  return (
    <View className="stats-content-wrapper">
      {/* SECTION 1: HERO SUMMARY */}
      <View className="hero-summary-grid">
        <View className="summary-card-v2">
          <Text className="card-label">{t.stats_overall}</Text>
          <Text className="card-value">{stats.historyAvg}%</Text>
          <Text className={`card-trend ${stats.recentScore >= stats.historyAvg ? 'up' : 'down'}`}>
            {stats.recentScore >= stats.historyAvg ? '↑' : '↓'} {Math.abs(stats.recentScore - stats.historyAvg)}%
          </Text>
        </View>

        <View className="summary-card-v2">
          <Text className="card-label">{t.stats_practiced}</Text>
          <Text className="card-value">{stats.totalQuests}</Text>
          <Text className="card-sub-label">{lang === 'zh' ? '累计练习' : 'Questions Solved'}</Text>
        </View>

        <View className="summary-card-v2">
          <Text className="card-label">{lang === 'zh' ? '最强领域' : 'Strongest Topic'}</Text>
          <Text className="card-value-small">{stats.strongestSubject.name || (lang === 'zh' ? '思维推理' : 'Reasoning')}</Text>
          <Text className="card-sub-label">{stats.strongestSubject.avg}% {t.accuracy_label}</Text>
        </View>

        <View className="summary-card-v2">
          <Text className="card-label">{lang === 'zh' ? '有待加强' : 'Needs Practice'}</Text>
          <Text className="card-value-small">{stats.weakestTopic.topic || stats.weakestTopic.name || (lang === 'zh' ? '综合思维' : 'General')}</Text>
          <Text className="card-sub-label" style={{ color: '#ef4444' }}>
            {stats.weakestTopic.avg}% {t.accuracy_label}
          </Text>
        </View>
      </View>

      {/* SECTION 2: PROGRESS TREND */}
      <View className="section-container">
        <View className="section-header-row">
          <Text className="section-title-v2">{lang === 'zh' ? '成长趋势' : 'Progress Trend'}</Text>
          <View className="filter-pills">
            {(['Last Runs', '7D', '30D', 'All Time'] as const).map(f => (
              <Text
                key={f}
                className={`pill ${trendFilter === f ? 'active' : ''}`}
                onClick={() => setTrendFilter(f)}
              >
                {trendLabels[f]}
              </Text>
            ))}
          </View>
        </View>

        <View className="chart-container-v2">
          {stats.trendData.length > 0 ? (
            <View className="bar-chart-v2">
              {stats.trendData.map((d, i) => (
                <View key={i} className="bar-wrapper">
                  <View
                    className="bar-fill"
                    style={{ height: `${Math.max(12, d.value)}%`, backgroundColor: getMetricColor(d.value) }}
                  >
                    <Text className="bar-val-text">{d.value}%</Text>
                  </View>
                  {d.label && <Text className="bar-label-text">{d.label}</Text>}
                </View>
              ))}
            </View>
          ) : (
            <Text className="no-data-text">
              {lang === 'zh' ? '该时段数据不足' : 'Complete more rounds to see your trend'}
            </Text>
          )}
        </View>
      </View>

      {/* SECTION 3: TOPIC PERFORMANCE */}
      <View className="section-container">
        <Text className="section-title-v2">{t.subject_stats}</Text>
        <View className="subject-grid-v2">
          {stats.subjectBreakdown.map((s, i) => (
            <View
              key={i}
              className="subject-card-v2"
              onClick={() => startPracticeWithFilters(s.filters)}
            >
              <View className="subject-info-v2">
                <Text className="subj-name">{s.name}</Text>
                <Text className="subj-count">{s.count} {questionUnit}</Text>
              </View>
              <View className="subj-acc-v2">
                <Text className="acc-text" style={{ color: getMetricColor(s.avg) }}>
                  {s.avg}%
                </Text>
                <View className="acc-bar-mini">
                  <View
                    className="fill"
                    style={{ width: `${s.avg}%`, backgroundColor: getMetricColor(s.avg) }}
                  />
                </View>
              </View>
            </View>
          ))}
        </View>
      </View>

      {/* SECTION 4: WEAK TOPICS & REDO */}
      <View className="section-container">
        <View className="section-header-row">
          <Text className="section-title-v2">{t.weak_topics}</Text>
          {wrongCount > 0 && (
            <View className="redo-btn-inline" onClick={handleRedoWrong}>
              <Text className="redo-text">📝 {t.redo_wrong.replace('{{count}}', String(wrongCount))}</Text>
            </View>
          )}
        </View>
        {stats.focusAreas && stats.focusAreas.length > 0 ? (
          <View className="weak-list-v2">
            {stats.focusAreas.map((a, i) => (
              <View key={i} className="weak-row-v2" onClick={() => startPracticeWithFilters(a.filters)}>
                <View className="weak-info-v2">
                  <Text className="weak-name">{a.name}</Text>
                  <Text className="weak-acc">{a.avg}% {t.accuracy_label}</Text>
                </View>
                <View className="weak-bar-mini">
                  <View className="fill" style={{ width: `${a.avg}%`, backgroundColor: getMetricColor(a.avg) }} />
                </View>
                <Text className="btn-train-v2">{lang === 'zh' ? '针对训练' : 'Train'}</Text>
              </View>
            ))}
          </View>
        ) : (
          <Text className="no-data-text">{lang === 'zh' ? '暂无薄弱领域——继续保持！' : 'No weak areas yet — keep it up!'}</Text>
        )}
      </View>
    </View>
  )
}
