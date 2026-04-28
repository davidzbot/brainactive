/**
 * BrainActive Data Utils - Bilingual Support
 */
import { getLang } from './storage'

const zhData = {
  names: [
    '张大伯','王大妈','李老师','赵班长','孙医生','陈会计','刘叔叔','周奶奶','谢师傅','谭大姐',
    '刘备','关羽','张飞','诸葛亮','曹操','孙权','周瑜','司马懿','孙悟空','唐僧',
    '猪八戒','沙僧','宋江','林冲','武松','鲁智深','李逵','贾宝玉','林黛玉','薛宝钗'
  ],
  cities: [
    '北京','上海','广州','深圳','成都','杭州','南京','重庆','西安','武汉',
    '苏黎世','伦敦','巴黎','东京','纽约','悉尼','新加坡','柏林','吉隆坡','曼谷',
    '首尔','台北','香港','澳门','拉萨','乌鲁木齐','哈尔滨','青岛','大连','厦门',
    '白鹤山','黄鹤楼','姚家村','文登','平乐','海底捞'
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
    { t: "多吃水果蔬菜对身体有益", w: "多吃水果梳菜对身体有益" }
  ],
  tips: [
    "大脑不用，会慢慢'生锈' 🧠",
    "多喝水，不然脑子容易'卡顿中…'",
    "多吃蔬菜，别让大脑变成油腻系统。",
    "动一动，大脑才不会进入'待机模式'。",
    "睡好一点，你的大脑也想下班。",
    "多和人聊天，大脑会更活跃。",
    "尝试新事物，大脑喜欢新刺激。",
    "散步10分钟，比发呆更有用。",
    "少刷短视频，大脑更清醒。",
    "记一点东西，大脑就不会偷懒。",
    "笑一笑，大脑会更放松。",
    "听听音乐，让思维更流畅。",
    "规律作息，大脑更稳定。",
    "少熬夜，大脑不喜欢加班。",
    "专注一件事，比多任务更聪明。"
  ]
};

const enData = {
  names: [
    'Uncle Bob', 'Auntie May', 'Professor Snape', 'Captain Jack', 'Dr. Strange', 'Agent Smith', 'Master Yoda', 'Granny Smith', 'Sherlock', 'Wonder Woman',
    'Iron Man', 'Thor', 'Hulk', 'Black Widow', 'Batman', 'Superman', 'Joker', 'Frodo', 'Gandalf', 'Harry Potter',
    'Dobby', 'Gollum', 'Elon Musk', 'Steve Jobs', 'Bill Gates', 'Taylor Swift', 'Beyonce', 'Mickey Mouse', 'Donald Duck', 'SpongeBob',
    'Chewbacca', 'Pikachu', 'Baby Yoda', 'Gordon Ramsay', 'Rick Sanchez', 'Morty Smith', 'Walter White', 'Jack Sparrow', 'Katniss Everdeen', 'Indiana Jones'
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
    { t: "I'm on a seafood diet. I see food and I eat it", w: "I'm on a seafood diet. I see food and I eate it" },
    { t: "The quick brown fox jumps over the lazy dog", w: "The quick brown fox jumps over the laxy dog" },
    { t: "Yesterday I was clever, so I wanted to change the world", w: "Yesterday I was clevver, so I wanted to change the world" }
  ],
  tips: [
    "Use it or lose it! Your brain isn't a museum piece 🧠",
    "Hydrate! A dry brain is basically a raisin in a skull 💧",
    "Eat your greens, unless you want a potato-powered brain 🥦",
    "Move a bit! Don't let your brain enter 'Infinite Loading' mode ⚡",
    "Sleep well. Your brain needs to uninstall the day's junk 😴",
    "Chat more! Socializing is like a software update for your mind 🗣️",
    "Try new things. Your brain loves spicy new experiences 🌶️",
    "A 10-minute walk is better than staring at a wall for an hour 🚶",
    "Put down the phone. Doom-scrolling is not a sport 📱",
    "Memorize something! Don't let your brain become a floppy disk 💾",
    "Smile! It confuses your brain into thinking you're happy 😄",
    "Listen to music. Let your thoughts have a dance party 🎵",
    "Stick to a routine. Your brain loves a good script 📅",
    "Stop the all-nighters. Your brain doesn't get paid for overtime 🌙",
    "Focus! Multitasking is just a way to mess up multiple things at once 🎯"
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
