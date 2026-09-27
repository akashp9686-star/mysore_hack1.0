const SUPABASE_READY = typeof window.supabase !== 'undefined' && !window.SUPABASE_URL.includes('YOUR_') && !window.SUPABASE_PUBLISHABLE_KEY.includes('YOUR_');
const supabaseClient = SUPABASE_READY ? window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_PUBLISHABLE_KEY) : null;

function getDemoProfile(){
  try { return JSON.parse(localStorage.getItem('pl_profile') || 'null'); } catch { return null; }
}
function saveProfile(profile){ localStorage.setItem('pl_profile', JSON.stringify(profile)); }
async function currentAuth(){
  if (!supabaseClient) return null;
  const {data} = await supabaseClient.auth.getSession();
  return data?.session?.user || null;
}
async function signInGoogle(){
  if (!supabaseClient) throw new Error('Google login is not configured yet. Add your Supabase URL and publishable key in frontend/supabase-config.js.');
  const redirectTo = `${location.origin}/path.html`;
  const {error} = await supabaseClient.auth.signInWithOAuth({provider:'google', options:{redirectTo, queryParams:{prompt:'select_account'}}});
  if(error) throw error;
}
async function signOut(){
  if(supabaseClient) await supabaseClient.auth.signOut();
  localStorage.removeItem('pl_profile');
  localStorage.removeItem('hackmysore_student_id');
  localStorage.removeItem('last_ai_analysis');
  localStorage.removeItem('last_concept_id');
  localStorage.removeItem('active_intervention_id');
  localStorage.removeItem('intervention_baseline_accuracy');
  sessionStorage.removeItem('pl_ai_greeted_session');
  location.href='index.html';
}
async function ensureEntry(){
  const user = await currentAuth();
  if(user) return {user, profile:getDemoProfile()};
  const profile = getDemoProfile();
  if(profile) return {user:null, profile};
  location.href='index.html';
  return null;
}
window.Auth={supabase:supabaseClient,ready:SUPABASE_READY,currentAuth,signInGoogle,signOut,getDemoProfile,saveProfile,ensureEntry};
