// Component for dragging and dropping images which will be sent to ML Model for detection
"use client";
import LeafSVG from "@/components/assets/Leaf";
import { Button } from "@/components/ui/button";
import { ChangeEvent, FormEvent, useState } from "react";
import { useToast } from "@/components/ui/use-toast";
import Image from "next/image";
import { useQuery } from "@tanstack/react-query";
import Result from "@/components/result";
import { ReloadIcon } from "@radix-ui/react-icons";
import axios from "axios";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
interface FormData {
    images: (string | ArrayBuffer | null)[];
    similar_images: boolean;
}

export function ImageBox() {
    const [imageFile, setImageFile] = useState<File | null>(null);
    const [formData, setFormData] = useState<FormData[]>([]);
    const [imageURL, setImageURL] = useState<string>();
    const { toast } = useToast();

    const [plantName, setPlantName] = useState("");
    console.log(plantName);
    const plantList = [
        "Tomato",
        "Potato",
        "Apple",
        "Grape",
        "Pepper,_bell",
        "Peach",
        "Strawberry",
        "Cherry",
        "Corn",
    ];

    const [resultData, setResultData] = useState<any>(null);
    const [isInitialLoading, setIsInitialLoading] = useState(false);

    const uploadFile = async (e: ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setImageFile(file);
            const objectURL = URL.createObjectURL(file);
            setImageURL(objectURL);
        }
    };

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (imageFile) {
            const formData = new FormData();
            formData.append("file", imageFile);
            try {
                const resp = await axios.post(
                    "http://localhost:8000?plant_name=" + plantName,
                    formData,
                    {
                        headers: {
                            "Content-Type": "multipart/form-data",
                        },
                    }
                );
                const data = await resp.data;
                // const data = await resp.json();
                console.log(data);
                setResultData(data);
            } catch (error) {
                console.log(error);
            }
        }
    };

    return (
        <section className="mt-8 md:mt-4">
            <div id="google_translate_element"></div>
            <form
                encType="multipart/form-data"
                method="post"
                onSubmit={handleSubmit}
            >
                <div className="flex flex-col items-center">
                    <div>
                        <Label htmlFor="plant" className="text-xl m-8">
                            Plant Name
                        </Label>
                        <Select onValueChange={(e) => setPlantName(e)}>
                            <SelectTrigger className="mt-4">
                                <SelectValue placeholder="Select Plant" />
                            </SelectTrigger>
                            <SelectContent className="">
                                {plantList.map((plant, i) => (
                                    <SelectItem
                                        value={plant.toString()}
                                        key={i}
                                        onClick={() => setPlantName(plant)}
                                    >
                                        {plant}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <label htmlFor="plant-image" className="cursor-pointer">
                        <div className="relative w-72 mt-4 flex items-center justify-center aspect-square mx-auto border-2 dark:border-white border-black border-dashed rounded-lg">
                            {imageURL ? (
                                <Image
                                    src={imageURL}
                                    alt="Image"
                                    fill
                                    className="rounded-lg"
                                />
                            ) : (
                                <div className="flex flex-col gap-2 p-4 justify-center items-center">
                                    <LeafSVG />
                                    <p className="text-center">
                                        Upload Plant Image Here
                                    </p>
                                </div>
                            )}
                            <input
                                type="file"
                                name="plant-image"
                                id="plant-image"
                                className="hidden"
                                accept=".png, .jpeg, .jpg"
                                onChange={uploadFile}
                                required
                            />
                        </div>
                    </label>
                    <div className="mt-4">
                        {imageFile === null ? (
                            <Button disabled className="select-none">
                                Add Image to Proceed
                            </Button>
                        ) : (
                            <div className="flex flex-col justify-center gap-4 items-center">
                                <p>{imageFile.name} Uploaded!</p>
                                {/* Disable the button when the process is running or already previous data is there */}
                                <Button
                                    type="submit"
                                    disabled={isInitialLoading || resultData}
                                >
                                    {isInitialLoading && (
                                        <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
                                    )}
                                    Detect Disease
                                </Button>
                            </div>
                        )}
                    </div>
                </div>
            </form>
            {resultData ? <Result data={resultData} /> : ""}
        </section>
    );
}
