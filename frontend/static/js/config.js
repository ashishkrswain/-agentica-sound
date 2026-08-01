// Client configuration
const CONFIG = {
  TOKEN_KEY: "agentica_sound_token",
  USER_KEY: "agentica_sound_user",
  POLL_INTERVAL_MS: 3000,
};

function getToken() {
  return localStorage.getItem(CONFIG.TOKEN_KEY);
}

function setToken(token) {
  if (token) {
    localStorage.setItem(CONFIG.TOKEN_KEY, token);
  } else {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
  }
}

function getUser() {
  try {
    const raw = localStorage.getItem(CONFIG.USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function setUser(user) {
  if (user) {
    localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(CONFIG.USER_KEY);
  }
}

function clearSession() {
  localStorage.removeItem(CONFIG.TOKEN_KEY);
  localStorage.removeItem(CONFIG.USER_KEY);
}
