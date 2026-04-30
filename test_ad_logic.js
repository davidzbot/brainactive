
// Mock Taro and Storage for testing
const storage = {};
global.localStorage = {
  getItem: (k) => storage[k] || null,
  setItem: (k, v) => { storage[k] = String(v); },
  clear: () => { for (let k in storage) delete storage[k]; }
};

// Simplified versions of the logic
function getStorage(key) {
  const val = localStorage.getItem(key);
  try { return JSON.parse(val); } catch (e) { return val; }
}

function setStorage(key, val) {
  localStorage.setItem(key, JSON.stringify(val));
}

function isAdUnlocked() {
  const unlockUntil = getStorage('ad_unlock_until');
  if (!unlockUntil) return false;
  return Date.now() < unlockUntil;
}

function unlockAllModes() {
  const expiry = Date.now() + 24 * 60 * 60 * 1000;
  setStorage('ad_unlock_until', expiry);
}

function formatDate(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
}

function getDailyUsage(mode) {
  const usage = getStorage('daily_usage') || {};
  const today = formatDate(new Date());
  if (usage.date !== today) return 0;
  return usage[mode] || 0;
}

function incrementDailyUsage(mode) {
  const usage = getStorage('daily_usage') || {};
  const today = formatDate(new Date());
  if (usage.date !== today) {
    usage.date = today;
    usage.easy = 0; usage.normal = 0; usage.pro = 0;
  }
  usage[mode] = (usage[mode] || 0) + 1;
  setStorage('daily_usage', usage);
}

function canPlayMode(mode) {
  if (isAdUnlocked()) return true;
  return getDailyUsage(mode) < 1;
}

// Test cases
console.log("Initial state:");
console.log("Easy playable?", canPlayMode('easy')); // true

console.log("\nPlay Easy once:");
incrementDailyUsage('easy');
console.log("Easy playable?", canPlayMode('easy')); // false (locked)

console.log("\nWatch Ad:");
unlockAllModes();
console.log("Ad unlocked?", isAdUnlocked()); // true
console.log("Easy playable now?", canPlayMode('easy')); // true (unlocked by ad)

console.log("\nCheck 24h expiry (simulation):");
setStorage('ad_unlock_until', Date.now() - 1000); // Expired
console.log("Ad unlocked?", isAdUnlocked()); // false
console.log("Easy playable?", canPlayMode('easy')); // false
