<?php
/**
 * test case
 */
require_once dirname(__FILE__).'/../classautoloader.php';
/**
 * 
 */
class WURFL_Hanlders_MotorolaHandlerTest extends PHPUnit_Framework_TestCase {
	
	private $motorolaHandler;
	
	function setUp() {
		$context = new WURFL_Context ( null );
		$userAgentNormalizer = new WURFL_Request_UserAgentNormalizer_Null ();
		$this->motorolaHandler = new WURFL_Handlers_MotorolaHandler ( $context, $userAgentNormalizer );
	}
	
	public function testShouldNotHandle() {
		$userAgent = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)";
		$this->assertFalse ( $this->motorolaHandler->canHandle ( $userAgent ) );
	}
	
	public function testShouldHandle() {
		$userAgent = "Mozilla/5.0 (compatible;MSIE 6.0;Linux MOTOROKR Z6W-orange) MOT-Z6w/R6635_G_81.01.61R Profile/MIDP-2.0 Configuration/CLDC-1.1 Symphony 1.0";
		$this->assertTrue ( $this->motorolaHandler->canHandle ( $userAgent ) );
	}
}
