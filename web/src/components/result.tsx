interface ResultProps {
    data: any;
}

export default function Result({ data }: ResultProps) {
    console.log(data);
    const prediction = data;
    return (
        <div className="w-screen mt-8">
            {/* If the image is not a plant just show one line */}
            {prediction[0].is_plant ? (
                <div className="p-8 bg-secondary">
                    <p className="text-center text-3xl md:text-4xl">
                        Plant is{"  "}
                        <span className="font-bold">
                            {prediction.disease_name === "healthy" ? (
                                <span className="gradient-text">Healthy</span>
                            ) : (
                                <span className="text-red-500">Unhealthy</span>
                            )}
                        </span>
                    </p>
                    {/* If the plant is healthy display a motivated message :) */}
                    {prediction.disease_name === "healthy" && (
                        <p className="text-center mt-4 text-lg">
                            Your plant is happy, you are truly a nature lover!
                        </p>
                    )}
                    {/* If the plant is unhealthy then only display the diseases */}
                    {prediction.disease_name !== "healthy" && (
                        <div>
                            <p className="text-center text-lg md:text-2xl mt-8">
                                Potential Diseases
                            </p>
                            <div
                                className={`${
                                    prediction.length === 1
                                        ? ""
                                        : "md:grid-cols-1"
                                } grid gap-6 place-content-center`}
                            >
                                {prediction.map(
                                    (predicted: any) =>
                                        predicted.disease_name !==
                                            "healthy" && (
                                            <div
                                                className="mt-4 text-center grid md:grid-cols-2 place-items-center gap-4"
                                                key={predicted.disease_name}
                                            >
                                                <div className="">
                                                    <div className="flex items-center justify-center">
                                                        <p className="text-2xl font-bold">
                                                            {
                                                                predicted.disease_name
                                                            }
                                                            :{" "}
                                                            {(
                                                                predicted.confidence *
                                                                100
                                                            ).toPrecision(7)}
                                                            %
                                                        </p>
                                                    </div>
                                                    <p className="my-2">
                                                        Plants with{" "}
                                                        {predicted.disease_name}
                                                    </p>
                                                    {/* <div className="flex gap-2">
                                                {disease.similar_images.map(
                                                    (image) => (
                                                        <div key={image.id}>
                                                            <img
                                                                src={image.url}
                                                                alt={
                                                                    image.citation
                                                                }
                                                                className="rounded-md"
                                                            />
                                                            <p className="my-4">
                                                                Similarity:{" "}
                                                                <span className="font-bold">
                                                                    {(
                                                                        image.similarity *
                                                                        100
                                                                    ).toPrecision(
                                                                        4
                                                                    )}
                                                                    %
                                                                </span>
                                                            </p>
                                                        </div>
                                                    )
                                                )}
                                            </div> */}
                                                </div>
                                                {/* <div className="flex flex-col gap-4">
                                            <div>
                                                <h3 className="text-center font-bold text-xl mb-1">
                                                    Description
                                                </h3>
                                                <p className="text-justify">
                                                    {
                                                        disease.details
                                                            .description
                                                    }
                                                </p>
                                            </div>
                                            <div>
                                                <h3 className="text-center font-bold text-xl mb-1">
                                                    Treatment
                                                </h3>
                                                <div className="text-justify flex flex-col gap-2">
                                                    <p>
                                                        <span className="font-bold">
                                                            Chemical:
                                                        </span>{" "}
                                                        {
                                                            disease.details
                                                                .treatment
                                                                .chemical
                                                        }
                                                    </p>
                                                    <p>
                                                        <span className="font-bold">
                                                            Biological:
                                                        </span>{" "}
                                                        {
                                                            disease.details
                                                                .treatment
                                                                .biological
                                                        }
                                                    </p>
                                                </div>
                                            </div>
                                            <div>
                                                <h3 className="text-center font-bold text-xl mb-1">
                                                    Prevention
                                                </h3>
                                                <p className="text-justify">
                                                    {
                                                        disease.details
                                                            .treatment
                                                            .prevention
                                                    }
                                                </p>
                                            </div>
                                        </div> */}
                                            </div>
                                        )
                                )}
                            </div>
                        </div>
                    )}
                </div>
            ) : (
                <div className="text-center">
                    <p className="text-2xl">Image is not a Plant</p>
                    <p className="text-red-500 mt-1 text-lg">
                        Please put the correct image and retry!
                    </p>
                </div>
            )}
        </div>
    );
}
