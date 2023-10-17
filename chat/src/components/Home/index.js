import "./home.css";

const Home = () => {
  return (
    <div className="outerdiv">
      <div className="innerdiv">
        <iframe
          className="chatBot"
          allow="microphone;"
          width="400"
          height="500"
          src="https://console.dialogflow.com/api-client/demo/embedded/fada8c31-74f8-42c4-8b48-c8decfa744bb"
        ></iframe>
      </div>
    </div>
  );
};

export default Home;
