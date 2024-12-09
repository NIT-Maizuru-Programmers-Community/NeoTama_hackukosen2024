import { Input } from "@/components/ui/input";
import React from "react";
import { Button } from "./ui/button";
import { useState } from "react";
import { Link } from "react-router-dom";

const Add = () => {
	const [match, setMatch] = useState(false);
	return (
		<div>
			<div className='justify-between flex'>
				<Input className=' ml-2 my-2' />
				<Button className='mx-2 my-2'>検索</Button>
			</div>
			<div className='w-screen p-5'>
				{match ? (
					<Button className='w-full'>追加する</Button>
				) : (
					<Button className='w-full'>
						<Link to='/'>ホームに戻る</Link>
					</Button>
				)}
			</div>
		</div>
	);
};

export default Add;
