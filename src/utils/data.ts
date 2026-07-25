/**
 * BrainActive Data Utils - Bilingual Support
 */
import { getLang } from './storage'

const zhData = {
  names: [
    '张大伯','王大妈','李老师','赵班长','孙医生','陈会计','刘叔叔','周奶奶','谢师傅','谭大姐',
    '刘备','关羽','张飞','诸葛亮','曹操','孙权','周瑜','司马懿','孙悟空','唐僧',
    '猪八戒','沙僧','宋江','林冲','武松','鲁智深','李逵','贾宝玉','林黛玉','薛宝钗',
    '小明','小红','阿呆','阿瓜','喜羊羊','灰太狼','超级飞侠','奥特曼','柯南','哆啦A梦'
  ],
  cities: [
    '北京','上海','广州','深圳','成都','杭州','南京','重庆','西安','武汉',
    '苏黎世','伦敦','巴黎','东京','纽约','悉尼','新加坡','柏林','吉隆坡','曼谷',
    '首尔','台北','香港','澳门','拉萨','乌鲁木齐','哈尔滨','青岛','大连','厦门',
    '西湖','黄山','泰山','桂林','九寨沟','张家界','故宫','长城','西双版纳','三亚'
  ],
  sentences: [
    { t: "今天早上去市场买新鲜蔬菜", w: "今天早上去市厂买新鲜蔬菜" },
    { t: "下午在公园慢慢散步放松心情", w: "下午在公圆慢慢散步放松心情" },
    { t: "晚上和朋友一起聊天喝茶", w: "晚上和明友一起聊天喝茶" },
    { t: "周末带家人出去吃饭放松", w: "周末带家人出去契饭放松" },
    { t: "早上锻炼身体让精神更好", w: "早上锻陈身体让精神更好" },
    { t: "晚饭后散步有助于健康", w: "晚饭后散步有助干健康" },
    { t: "读书可以提升记忆能力", w: "读书可以提升记意能力" },
    { t: "规律作息让大脑更清醒", w: "规律作息让大脑更情醒" },
    { t: "坚持运动能增强身体素质", w: "坚持运动能增虽身体素质" },
    { t: "多吃水果蔬菜对身体有益", w: "多吃水果梳菜对身体有益" },
    { t: "爷爷和小孙子一起在客厅看书", w: "爷爷和小孙子一起在客厅看书" },
    { t: "每天做三分钟脑力操预防痴呆", w: "每天做三分中脑力操预防痴呆" }
  ],
  tips: [
    "大脑越用越灵活，天天练习防衰老 🧠",
    "多喝温开水，保持大脑水分充沛 💧",
    "多吃深色蔬菜，保护脑神经健康 🥦",
    "每天散步20分钟，促进脑部血液循环 🚶",
    "保证充足睡眠，让大脑彻底休息 😴",
    "多与儿女长辈交流，思维更敏捷 🗣️",
    "学习一项新技能，激发大脑新活力 🌟",
    "保持好心情，欢笑是最好的健脑药 😄",
    "少刷无用短视频，专注思考更健康 📱",
    "每天记几个新词，训练短期记忆力 💾"
  ]
};

const enData = {
  names: [
    'Uncle Bob', 'Auntie May', 'Professor Snape', 'Captain Jack', 'Dr. Strange', 'Agent Smith', 'Master Yoda', 'Granny Smith', 'Sherlock', 'Wonder Woman',
    'Iron Man', 'Thor', 'Hulk', 'Black Widow', 'Batman', 'Superman', 'Joker', 'Frodo', 'Gandalf', 'Harry Potter',
    'Dobby', 'Gollum', 'Elon Musk', 'Steve Jobs', 'Bill Gates', 'Taylor Swift', 'Beyonce', 'Mickey Mouse', 'Donald Duck', 'SpongeBob',
    'Chewbacca', 'Pikachu', 'Baby Yoda', 'Gordon Ramsay', 'Mario', 'Luigi', 'Sonic', 'Spiderman', 'Elsa', 'Olaf'
  ],
  cities: [
    'New York', 'London', 'Paris', 'Tokyo', 'Sydney', 'Beijing', 'Singapore', 'Berlin', 'Dubai', 'Toronto',
    'Hogwarts', 'Gotham City', 'Metropolis', 'Neverland', 'Middle Earth', 'Mars', 'The Moon', 'Atlantis', 'Wakanda', 'Springfield',
    'Silicon Valley', 'Las Vegas', 'Hollywood', 'Wall Street', 'Amazon Rainforest', 'Mount Everest', 'Bermuda Triangle', 'Grand Canyon', 'Sahara Desert', 'North Pole',
    'Asgard', 'Rivendell', 'Winterfell', 'King\'s Landing', 'The Shire', 'Narnia', 'Pandora', 'Death Star', 'Tatooine', 'Zootopia'
  ],
  sentences: [
    { t: "My cat is judging my life choices again", w: "My cat is judging my life choises again" },
    { t: "I came into this room and forgot why", w: "I came into this room and forgot whyy" },
    { t: "Coffee: because adulting is hard without it", w: "Cofee: because adulting is hard without it" },
    { t: "I'm not lazy, I'm on energy saving mode", w: "I'm not lazy, I'm on energy savin mode" },
    { t: "My brain has too many tabs open right now", w: "My brain has too meny tabs open right now" },
    { t: "I put the 'pro' in procrastination today", w: "I put the 'pro' in procrustination today" },
    { t: "Life is short, smile while you still have teeth", w: "Life is short, smile while you stil have teeth" },
    { t: "Grandpa and kids are playing brain games", w: "Grandpa and kids are playin brain games" },
    { t: "Daily 3 minutes of exercises keeps dementia away", w: "Daily 3 minutes of exercises keeps dementya away" }
  ],
  tips: [
    "Use it or lose it! Keep your brain active daily 🧠",
    "Hydrate! Your brain needs water to stay sharp 💧",
    "Eat fresh greens to protect your brain neurons 🥦",
    "A 20-minute daily walk boosts brain oxygen 🚶",
    "Quality sleep resets and sharpens your mind 😴",
    "Chat with family & grandkids for mental agility 🗣️",
    "Learn something new to stimulate fresh neural pathways 🌟",
    "Laughter relaxes your mind and reduces stress 😄",
    "Limit mindless scrolling; focus on active thinking 📱"
  ]
};

export const dataUtils = {
  get names() {
    return getLang() === 'zh' ? zhData.names : enData.names;
  },
  get cities() {
    return getLang() === 'zh' ? zhData.cities : enData.cities;
  },
  get sentences() {
    return getLang() === 'zh' ? zhData.sentences : enData.sentences;
  },
  get tips() {
    return getLang() === 'zh' ? zhData.tips : enData.tips;
  }
};
