import axios from 'axios';
import { API_BASE_URL } from '../config';
import { getSession } from './session';

// Fail fast if the backend is unreachable (e.g. wrong IP or backend not running)
axios.defaults.timeout = 2000;

export const createUser = async (data: {
    name?: string;
    email: string;
    password: string;
    contactEmail?: string;
    countryCode?: string;
    phone?: string;
    diversityType?: string;
}) => {
    const payload = {
        name: data.name || null,
        email: data.email,
        password: data.password,
        contact_person_email: data.contactEmail || null,
        contact_person_country_code: data.countryCode || null, //Send it like string because of this problem in backend if it is INT : 001 => 1
        contact_person_phone_number: data.phone || null, //Same as country code problem
        diversity_type: data.diversityType || null,
    }

    const response = await axios.post(`${API_BASE_URL}/users/`, payload)
    return response.data; 
};

export const login = async (email: string, password: string) =>{
    const response = await axios.post(`${API_BASE_URL}/auth/session`, {
        email,
        password
    });
    return response.data; //Returns Object of type LoginResponse (session_id,user)
}

export const getCurrentUser = async (sessionId: string) => {
    const response = await axios.get(`${API_BASE_URL}/auth/me`,{
        headers: {
            'authorization': sessionId
        }
    });
    return response.data; // Returns Object of type UserResponse
};

export const logout = async (sessionId: string) =>{
    const response = await axios.post(`${API_BASE_URL}/auth/logout`,{},{
        headers: {
            'authorization': sessionId
        }
    });
    return response.data; //Returns status code 404.
}

export const deleteAccount = async (): Promise<void> => {
  const sessionId = await getSession();
  if (!sessionId) {
    throw new Error('No session found');
  }

  await axios.delete(`${API_BASE_URL}/users/me`, {
    headers: {
      'authorization': sessionId,
    },
  });
};

export const updateProfile = async (updates: Partial<{
  name: string;
  email: string;
  password: string;
  contact_person_email: string;
  contact_person_country_code: string;
  contact_person_phone_number: string;
  diversity_type: string;
}>) => {
  const sessionId = await getSession();
  if (!sessionId) {
    throw new Error('No session found');
  }

  const response = await axios.patch(
    `${API_BASE_URL}/users/me`,
    updates,
    {
      headers: {
        'authorization': sessionId,
        'Content-Type': 'application/json',
      },
    }
  );

  return response.data;
};

export const changePassword = async (currentPassword: string, newPassword: string) => {
    const sessionId = await getSession();
    if (!sessionId){
        throw new Error('No session found');
    }

    const response = await axios.patch(
        `${API_BASE_URL}/users/me/password`,
        {
            current_password: currentPassword,
            new_password: newPassword
        },
        {
            headers: {
                'authorization' : sessionId,
            },
        }
    );

    return response.data
}