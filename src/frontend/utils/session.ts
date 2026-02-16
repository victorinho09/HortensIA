import AsyncStorage from "@react-native-async-storage/async-storage";

const SESSION_KEY = '@hortensia:session_id';

export const saveSession = async (sessionId: string): Promise<void> => {
    try{
        await AsyncStorage.setItem(SESSION_KEY,sessionId);
    } catch (error){
        console.error('Error saving session: ', error);
        throw error;
    } 
};

export const getSession = async (): Promise<string | null> =>{
    try{
        return await AsyncStorage.getItem(SESSION_KEY);
    } catch(error){
        console.error('Error getting session: ',error);
        return null;
    }
};

export const clearSession = async (): Promise<void> =>{
    try{
        await AsyncStorage.removeItem(SESSION_KEY);
    }catch(error){
        console.error('Error clearing session: ', error);
        throw error;
    }
};