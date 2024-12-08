import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
	apiKey: "AIzaSyBNDZYUqItirSv8GuDu_78G6URAHioXjSo",
	authDomain: "neotama-bf737.firebaseapp.com",
	projectId: "neotama-bf737",
	storageBucket: "neotama-bf737.firebasestorage.app",
	messagingSenderId: "448904035572",
	appId: "1:448904035572:web:472a0f1d3c4c53ad8232a1",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { auth };
