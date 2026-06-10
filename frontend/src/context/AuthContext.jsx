import { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check active sessions and sets the user
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        formatAndSetUser(session.user);
      }
      setLoading(false);
    });

    // Listen for changes on auth state (log in, log out, etc.)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        formatAndSetUser(session.user);
      } else {
        setUser(null);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const formatAndSetUser = (supabaseUser) => {
    const email = supabaseUser.email;
    const namePart = email.split('@')[0];
    const formattedName = namePart.charAt(0).toUpperCase() + namePart.slice(1).replace(/[^a-zA-Z0-9]/g, ' ');
    
    setUser({
      id: supabaseUser.id,
      name: formattedName,
      email: email,
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${formattedName}`
    });
  };

  const login = async (email, password) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw new Error(error.message);
  };

  const signup = async (email, password) => {
    const { error } = await supabase.auth.signUp({
      email,
      password,
    });
    if (error) throw new Error(error.message);
  };

  const logout = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) throw new Error(error.message);
  };

  const migrateLocalStorageUsers = async () => {
    try {
      const users = JSON.parse(localStorage.getItem('emailiq_users') || '[]');
      if (users.length === 0) {
        alert("No local users found to migrate.");
        return;
      }

      let successCount = 0;
      let failCount = 0;

      for (const u of users) {
        if (!u.email || !u.password) {
          failCount++;
          continue;
        }
        
        const { error } = await supabase.auth.signUp({
          email: u.email,
          password: u.password,
        });

        if (error) {
          console.error("Migration error for", u.email, error.message);
          failCount++;
        } else {
          successCount++;
        }
      }

      alert(`Migration complete!\nSuccessfully migrated: ${successCount}\nFailed/Skipped: ${failCount}\n\nNote: Supabase requires unique emails and 6+ character passwords. If you had 'test' users with weak passwords, they may have failed to migrate.`);
      
      // Clear local storage after successful migration attempt
      localStorage.removeItem('emailiq_users');
      localStorage.removeItem('emailiq_user');

    } catch (err) {
      alert("Error migrating users: " + err.message);
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, migrateLocalStorageUsers }}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
