import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuthState } from "react-firebase-hooks/auth";
import { auth } from "@/lib/firebase";
import Login from "@/components/Login";
import Home from "@/components/Home";
import Add from "./components/Add";

function App() {
	const [user] = useAuthState(auth);
	return (
		<BrowserRouter>
			<Routes>
				<Route path='/' element={<Home />} />
				<Route path='/login' element={user ? <Navigate to='/' /> : <Login />} />
				<Route
					path='/add'
					element={user ? <Add /> : <Navigate to='/login' />}
				/>
			</Routes>
		</BrowserRouter>
	);
}

export default App;
