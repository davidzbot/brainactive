/**
 * Professional Bilingual Support
 * Tone: Calm, Professional, Encouraging
 */
const zh: Record<string, string> = {
  'app.title': '大脑每日练 (BrainActive)',
  'app.subtitle': '防衰老 · 亲子同练 · 脑力常青',
  'app.description': '专为长辈防老年痴呆 & 孩子大脑开发设计的科学练脑工具。每天 3 分钟，激活大脑活力，长辈脑力更年轻，孩子思维更敏捷！',
  'app.status.0': '今日未打卡！立即训练，给大脑做个 SPA',
  'app.status.low': '已连续打卡 {s} 天，脑力正在稳步提升',
  'app.status.mid': '已连续打卡 {s} 天，大脑反应更敏捷',
  'app.status.high': '已连续打卡 {s} 天，巅峰大脑状态！',
  
  'button.invite': '邀请家人/好友共享脑力',
  'invite.text': '我正在用【大脑每日练】进行大脑保健！预防老年痴呆，提升记忆力，推荐你和家里长辈/小孩一起练！',
  'app.unlimited': '全功能访问已开启',
  'app.unlock_desc': '观看一段短视频，免费解锁 24 小时全功能',
  'app.locked': '高级练习锁定中',
  'app.unlocked': '全功能已开启',
  'app.expires_in': '{h}小时{m}分 后到期',
  'button.watch_to_unlock': '点击解锁 24 小时无限练习',
  'button.watch_again': '再次观看 (延长有效期)',
  
  'difficulty.easy': '长辈防衰保洁 (极简高对比)',
  'difficulty.normal': '亲子/日常强化 (思维敏捷)',
  'difficulty.pro': '脑力王者挑战 (高强风暴)',
  
  'panel.title': '选择您的专属训练模式',
  'mode.done': '今日已练习',
  'mode.limit': '练习额度已达',
  
  'button.start': '进入训练',
  'button.share': '分享到家族群/朋友圈',
  'cta.ad': '开启完整访问',
  
  'task.title': '认知训练中',
  'task.loading': '正在准备训练项目...',
  'task.got_it': '我记住了！开始挑战',
  'task.back': '返回再看一眼',
  'task.exit': '退出训练',
  'task.exit_confirm': '确认退出？',
  'task.exit_msg': '当前的进度将不会被保存。',
  'task.order_them': '请按刚才出现的顺序选择',
  'task.pick_them': '请选出刚才出现的内容',
  'task.remember_names': '请专注并记住以下姓名',
  'task.remember_cities': '请专注并记住以下城市',
  'task.remember_numbers': '请专注并记住这些数字',
  'task.remember_numbers_calc': '请记住这些数字，稍后需进行计算',
  'task.remember_colorshapes': '请记住这些颜色和形状',
  'task.remember_sentences': '请仔细阅读并记住以下句子',
  
  'task.remember_names_seq': '请按顺序记住以下姓名',
  'task.remember_cities_seq': '请按顺序记住以下城市',
  'task.remember_colorshapes_seq': '请按顺序记住颜色和形状',
  'task.remember_sentences_seq': '请按顺序记住以下句子',
  
  'task.step_memorize': '第一步：仔细观察并记忆',
  'task.step_answer': '第二步：凭记忆准确选择',
  
  'result.title': '脑力健康评估报告',
  'result.score': '脑力评分',
  'result.time': '答题用时',
  'result.eval.low': '表现稳健！每天坚持练，预防衰老见效快。',
  'result.eval.mid': '思维活跃！记忆力与反应力都相当出色！',
  'result.eval.high': '大脑年龄比同龄人年轻 10 岁！状态太棒了！',
  'button.home': '返回主页',
  
  'tip.prefix': '💡 健脑小贴士：',
  'footer.feedback': '意见反馈: pslehero@gmail.com',
  'common.days': '天',
  'common.streak': '连续打卡'
};

const en: Record<string, string> = {
  'app.title': 'BrainActive',
  'app.subtitle': 'Dementia Prevention · Kids & Senior Brain Boost',
  'app.description': 'Scientific 3-minute brain exercises crafted to prevent Alzheimer\'s in seniors and boost cognitive focus in kids & families. Stay sharp together!',
  'app.status.0': 'Not checked in today! Train now for a brain SPA.',
  'app.status.low': '{s} day streak. Mental clarity is improving steadily.',
  'app.status.mid': '{s} day streak. Sharp reaction & high focus achieved!',
  'app.status.high': '{s} day streak. Peak brain condition!',
  
  'button.invite': 'Invite Family & Kids to Challenge',
  'invite.text': 'I am using BrainActive for daily brain exercises to boost memory & prevent cognitive decline. Join me with your family!',
  'app.unlimited': 'Full Access Active',
  'app.unlock_desc': 'Watch a short video to unlock 24-hour unlimited access',
  'app.locked': 'Features Locked',
  'app.unlocked': 'Full Access Active',
  'app.expires_in': 'Expires in {h}h {m}m',
  'button.watch_to_unlock': 'Watch Short Video to Unlock (24h)',
  'button.watch_again': 'Watch Again (Extend)',
  
  'difficulty.easy': 'Senior Vitality (Anti-Dementia)',
  'difficulty.normal': 'Kids & Family Boost (Quick Focus)',
  'difficulty.pro': 'Master Challenge (High Intensity)',
  
  'panel.title': 'Select Training Mode',
  'mode.done': 'Daily limit reached',
  'mode.limit': 'Exercise limit reached',
  
  'button.start': 'Begin Exercise',
  'button.share': 'Share to Family & Friends',
  'cta.ad': 'Unlock Full Access',
  
  'task.title': 'Cognitive Training',
  'task.loading': 'Preparing session...',
  'task.got_it': 'I Noted It! Start Task',
  'task.back': 'Back to Review',
  'task.exit': 'End Session',
  'task.exit_confirm': 'End training?',
  'task.exit_msg': 'Your current progress will not be saved.',
  'task.order_them': 'Select in the order they appeared',
  'task.pick_them': 'Identify the items shown earlier',
  'task.remember_names': 'Focus and memorize these names',
  'task.remember_cities': 'Focus and memorize these cities',
  'task.remember_numbers': 'Memorize the following numbers',
  'task.remember_numbers_calc': 'Memorize these numbers for calculation',
  'task.remember_colorshapes': 'Memorize these colors and shapes',
  'task.remember_sentences': 'Carefully read and memorize these sentences',

  'task.remember_names_seq': 'Memorize these names in order',
  'task.remember_cities_seq': 'Memorize these cities in order',
  'task.remember_colorshapes_seq': 'Memorize colors and shapes in order',
  'task.remember_sentences_seq': 'Memorize these sentences in order',
  
  'task.step_memorize': 'Step 1: Memorize Carefully',
  'task.step_answer': 'Step 2: Choose from Memory',

  'result.title': 'Brain Health Assessment',
  'result.score': 'Brain Score',
  'result.time': 'Duration',
  'result.eval.low': 'Steady progress! Daily practice effectively prevents memory loss.',
  'result.eval.mid': 'High alertness! Excellent memory and reaction speed!',
  'result.eval.high': 'Your brain age is 10 years younger than average! Fantastic!',
  'button.home': 'Return to Home',
  
  'tip.prefix': '💡 Brain Tip: ',
  'footer.feedback': 'Feedback: pslehero@gmail.com',
  'common.days': 'Days',
  'common.streak': 'Day Streak'
};

export const t = (key: string, params?: any): string => {
  const lang = (typeof localStorage !== 'undefined' ? localStorage.getItem('lang') : 'en') || 'en';
  const dict = lang === 'zh' ? zh : en;
  let val = dict[key] || key;
  if (params) {
    Object.keys(params).forEach(k => {
      val = val.replace(`{${k}}`, params[k]);
    });
  }
  return val;
};
