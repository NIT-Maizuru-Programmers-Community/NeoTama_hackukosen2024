import React from "react";

const Home = () => {
	return(
		<div className="home min-h-screen flex flex-col bg-gray-50">
			<header className="home-header bg-blue-600 text-white p-4 flex justify-between items-center">
				<h1>ネオたまライブラリー</h1>
				<botton className="login-botton bg-white text-blue-600 px-4 py-2 rounded-full shadow-md hover:bg-blue-100">login</botton>
			</header>
			<main className="main-photo flex flex-col items-center gap-6 p-4 flex-grow">
				<div className="photo-log">
				<img
				src="/IMG_20241016_154131.jpg"
				alt="サンプル写真"
			  className="photo-image flex flex-col items-center gap-6 p-4 flex-grow"/>
				</div>
				</main>

		</div>
		)
};

export default Home;
