// Simple i18n helper (3 languages)
export const translations = {
  uz: {
    // Common
    app_name: "Anonymous Match",
    loading: "Yuklanmoqda...",
    save: "Saqlash",
    cancel: "Bekor qilish",
    delete: "O'chirish",
    edit: "Tahrirlash",
    send: "Yuborish",
    back: "Orqaga",
    next: "Keyingi",
    finish: "Tugatish",
    yes: "Ha",
    no: "Yo'q",

    // Auth
    welcome: "Xush kelibsiz",
    choose_nickname: "Anonim nickname tanlang",

    // Profile
    my_profile: "Mening profilim",
    bio: "Bio",
    interests: "Qiziqishlar",
    photos: "Rasmlar",
    age: "Yosh",
    location: "Joylashuv",

    // Discover
    no_profiles: "Profil topilmadi",
    try_again: "Qayta urinish",

    // Match
    its_match: "Bu MATCH!",
    say_hello: "Salomlashishni boshlang",
    you_matched_with: "Siz va {name} bir-biringizga yoqdingiz!",

    // Chat
    type_message: "Xabar yozing...",
    online: "Online",
    typing: "yozmoqda...",
    last_seen: "Oxirgi faollik",

    // Premium
    premium: "Premium",
    upgrade: "Premiumga o'tish",
    get_premium: "Premium olish",
    unlimited_likes: "Cheksiz yoqtirishlar",
    see_who_viewed: "Kim ko'rganini bilish",
    boost_monthly: "Boost har oy",

    // Settings
    settings: "Sozlamalar",
    theme: "Mavzu",
    language: "Til",
    notifications: "Bildirishnomalar",
    privacy: "Maxfiylik",
    logout: "Tizimdan chiqish",
    help: "Yordam",

    // Errors
    error: "Xatolik",
    try_again_later: "Keyinroq urinib ko'ring",
  },
  ru: {
    app_name: "Anonymous Match",
    loading: "Загрузка...",
    save: "Сохранить",
    cancel: "Отмена",
    delete: "Удалить",
    edit: "Редактировать",
    send: "Отправить",
    back: "Назад",
    next: "Далее",
    finish: "Готово",
    yes: "Да",
    no: "Нет",
    welcome: "Добро пожаловать",
    choose_nickname: "Выберите анонимный никнейм",
    my_profile: "Мой профиль",
    bio: "О себе",
    interests: "Интересы",
    photos: "Фото",
    age: "Возраст",
    location: "Местоположение",
    no_profiles: "Профили не найдены",
    try_again: "Попробовать снова",
    its_match: "Это MATCH!",
    say_hello: "Начните общение",
    you_matched_with: "Вы и {name} понравились друг другу!",
    type_message: "Напишите сообщение...",
    online: "Онлайн",
    typing: "печатает...",
    last_seen: "Был(а)",
    premium: "Премиум",
    upgrade: "Перейти на Премиум",
    get_premium: "Получить Премиум",
    unlimited_likes: "Безлимитные лайки",
    see_who_viewed: "Видеть кто смотрел",
    boost_monthly: "Буст каждый месяц",
    settings: "Настройки",
    theme: "Тема",
    language: "Язык",
    notifications: "Уведомления",
    privacy: "Приватность",
    logout: "Выйти",
    help: "Помощь",
    error: "Ошибка",
    try_again_later: "Попробуйте позже",
  },
  en: {
    app_name: "Anonymous Match",
    loading: "Loading...",
    save: "Save",
    cancel: "Cancel",
    delete: "Delete",
    edit: "Edit",
    send: "Send",
    back: "Back",
    next: "Next",
    finish: "Finish",
    yes: "Yes",
    no: "No",
    welcome: "Welcome",
    choose_nickname: "Choose an anonymous nickname",
    my_profile: "My Profile",
    bio: "Bio",
    interests: "Interests",
    photos: "Photos",
    age: "Age",
    location: "Location",
    no_profiles: "No profiles found",
    try_again: "Try again",
    its_match: "It's a MATCH!",
    say_hello: "Say hello",
    you_matched_with: "You and {name} liked each other!",
    type_message: "Type a message...",
    online: "Online",
    typing: "typing...",
    last_seen: "Last seen",
    premium: "Premium",
    upgrade: "Upgrade to Premium",
    get_premium: "Get Premium",
    unlimited_likes: "Unlimited likes",
    see_who_viewed: "See who viewed",
    boost_monthly: "Monthly boost",
    settings: "Settings",
    theme: "Theme",
    language: "Language",
    notifications: "Notifications",
    privacy: "Privacy",
    logout: "Log out",
    help: "Help",
    error: "Error",
    try_again_later: "Try again later",
  },
};

export type Lang = keyof typeof translations;
export const defaultLang: Lang = "uz";

export function t(key: string, lang: Lang = defaultLang, params?: Record<string, string>): string {
  let str = (translations[lang] as any)[key] || (translations.uz as any)[key] || key;
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      str = str.replace(`{${k}}`, v);
    });
  }
  return str;
}
