import axios from 'axios';
import { API_BASE_URL } from '../config';

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